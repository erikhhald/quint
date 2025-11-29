import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from openai import AsyncOpenAI

from database.database import db
from database.file_store import load_file
from database.models import Card
from settings.settings import settings

from .prompts import JUDGE_ANSWER_PROMPT, KEY_IDEAS_PROMPT
from .schemas import JUDGE_ANSWER_SCHEMA, KEY_IDEAS_SCHEMA


def get_card_from_deck(deck_id):
    # Calculate 24 hours from now
    now = datetime.now(timezone.utc)
    twenty_four_hours_later = now + timedelta(hours=24)

    # Query cards that are due within the next 24 hours, ordered by due time (soonest first)
    card = (
        db.session.query(Card)
        .filter(Card.deck_id == deck_id, Card.due <= twenty_four_hours_later)
        .order_by(Card.due)
        .first()
    )

    if not card:
        raise ValueError(
            f"No cards found in deck {deck_id} that are due within the next 24 hours"
        )

    return card.id


async def run_card(card_id, worker):
    # Get card from database
    card = db.session.query(Card).filter(Card.id == card_id).first()
    if not card:
        raise ValueError(f"Card not found: {card_id}")

    # Load file content using load_file
    if card.is_external:
        # External file - read directly from path
        try:
            with open(card.path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            raise IOError(f"Failed to read external file: {e}")
    else:
        # Internal file - use load_file with relative path
        relative_path = Path(card.path).name
        content = load_file(relative_path, internal=True)

    # Generate key ideas to get the topic
    result = await generate_key_ideas(content)
    topic = result.get("topic", "this topic")

    key_ideas = [elem for elem in result.get("key_ideas", [])]

    # Clear previous messages and add the final topic question
    worker.clear_chat.emit()
    worker.message_ready.emit(f"Tell me what you remember about: {topic}", False)
    worker.scroll_to_bottom.emit()

    # Loop until all key ideas are covered or max attempts reached
    max_attempts = 5
    attempt = 0
    remaining_key_ideas = key_ideas.copy()

    while remaining_key_ideas and attempt < max_attempts:
        attempt += 1

        # Wait for user response
        user_response = await worker.wait_for_user_input()
        print(user_response)

        # Judge the answer against remaining key ideas
        result = await judge_answer(user_response, remaining_key_ideas)
        understood_titles = result.get("key_ideas_answered", [])

        print(understood_titles)

        # Remove understood key ideas from the remaining list
        remaining_key_ideas = [
            idea
            for idea in remaining_key_ideas
            if idea["title"] not in understood_titles
        ]

        # Provide feedback to user
        if understood_titles:
            worker.message_ready.emit(
                f"Great! You demonstrated understanding of: {', '.join(understood_titles)}",
                False,
            )
        else:
            worker.message_ready.emit(
                "I didn't see clear evidence of understanding the key concepts. Let's try again!",
                False,
            )

        # If there are still remaining ideas and attempts left, ask again
        if remaining_key_ideas and attempt < max_attempts:
            remaining_titles = [idea["title"] for idea in remaining_key_ideas]
            worker.message_ready.emit(
                f"Let's focus on these concepts: {', '.join(remaining_titles)}. What else can you tell me?",
                False,
            )

        worker.scroll_to_bottom.emit()

    # Final summary
    if not remaining_key_ideas:
        worker.message_ready.emit(
            "Excellent! You've demonstrated understanding of all key concepts!", False
        )
    else:
        remaining_titles = [idea["title"] for idea in remaining_key_ideas]
        worker.message_ready.emit(
            f"Good session! You might want to review these concepts: {', '.join(remaining_titles)}",
            False,
        )

    worker.scroll_to_bottom.emit()

    return content


async def judge_answer(user_response, key_ideas):
    """
    Judge the user's answer against the study material.

    Args:
        user_response: The user's response to the topic question
        key_ideas: List of key ideas dictionaries with 'title' and 'description'
    """
    if not settings.openai_api_key:
        raise ValueError("OpenAI API key is required. Set it in settings.")

    # Extract key idea titles for the schema enum
    key_idea_titles = [idea["title"] for idea in key_ideas]

    # Format key ideas for the prompt
    key_ideas_text = ""
    for i, idea in enumerate(key_ideas, 1):
        key_ideas_text += f"{i}. **{idea['title']}**: {idea['description']}\n\n"

    # Create dynamic schema with the specific key idea titles
    judge_schema = JUDGE_ANSWER_SCHEMA.copy()
    judge_schema["properties"]["key_ideas_answered"]["items"]["enum"] = key_idea_titles

    client = AsyncOpenAI(api_key=settings.openai_api_key)

    response = await client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {
                "role": "user",
                "content": JUDGE_ANSWER_PROMPT.format(
                    answer=user_response, key_ideas=key_ideas_text
                ),
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "judge_answer_evaluation",
                "schema": judge_schema,
            },
        },
    )

    content = response.choices[0].message.content

    print(content)

    if not content:
        return {"key_ideas_answered": []}

    result = json.loads(content)
    return result


async def generate_key_ideas(markdown_text):
    if not settings.openai_api_key:
        raise ValueError("OpenAI API key is required. Set it in settings.")

    client = AsyncOpenAI(api_key=settings.openai_api_key)

    response = await client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "user", "content": KEY_IDEAS_PROMPT.format(text=markdown_text)}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "key_ideas_extraction",
                "schema": KEY_IDEAS_SCHEMA,
            },
        },
    )

    content = response.choices[0].message.content
    if not content:
        return {"topic": "", "key_ideas": []}
    result = json.loads(content)
    return result


async def process_study_card(deck_id, worker):
    """
    Asynchronously process a study card - load content and generate topic message.

    Args:
        deck_id: ID of the deck to get card from
        worker: Worker thread with signals to update UI
    """
    try:
        # Get a card from the deck
        card_id = get_card_from_deck(deck_id)

        # Clear chat and add loading message
        worker.clear_chat.emit()
        worker.scroll_to_bottom.emit()

        # Get the card content asynchronously - this now handles everything
        await run_card(card_id, worker)

    except Exception as e:
        # Clear any loading messages and show error
        worker.clear_chat.emit()
        worker.message_ready.emit(f"Error loading study material: {str(e)}", False)
        worker.scroll_to_bottom.emit()
        raise
