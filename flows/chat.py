import json

from openai import OpenAI

from settings.settings import settings

from .prompts import KEY_IDEAS_PROMPT
from .schemas import KEY_IDEAS_SCHEMA


def generate_key_ideas(markdown_text):
    """
    Generate key ideas from markdown text using OpenAI's API.

    Args:
        markdown_text: The markdown content to extract key ideas from
        api_key: Optional OpenAI API key. If not provided, uses OPENAI_API_KEY env var

    Returns:
        List of dictionaries with 'title' and 'description' keys

    Raises:
        ValueError: If no API key is provided

    """
    if not settings.openai_api_key:
        raise ValueError("OpenAI API key is required. Set it in settings.")

    client = OpenAI(api_key=settings.openai_api_key)

    response = client.chat.completions.create(
        model="gpt-5.1-mini",
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
        return []
    result = json.loads(content)
    return result.get("key_ideas", [])
