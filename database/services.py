from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from sqlalchemy import and_

from settings.settings import settings

from .database import db
from .models import Card, Deck
from .utilities import write_to_managed_store


def get_today_end():
    return datetime.now(timezone.utc).replace(
        hour=23, minute=59, second=59, microsecond=999999
    )


def get_cards_due_today(deck_id: int) -> List[Card]:
    """
    Get all cards from a deck that are due for review today.

    Args:
        deck_id: The ID of the deck to query

    Returns:
        List of Card objects due for review today
    """
    today_end = get_today_end()

    return (
        db.session.query(Card)
        .filter(and_(Card.deck_id == deck_id, Card.due <= today_end))
        .order_by(Card.due)
        .all()
    )


def get_new_cards(deck_id, limit=None):
    """
    Get new cards (never reviewed) from a deck.

    Args:
        deck_id: The ID of the deck to query
        limit: Maximum number of cards to return (optional)

    Returns:
        List of new Card objects
    """
    query = (
        db.session.query(Card)
        .filter(and_(Card.deck_id == deck_id, Card.state == 0))  # New cards
        .order_by(Card.created_at)
    )

    if limit:
        query = query.limit(limit)

    return query.all()


def count_new_cards(deck_id) -> int:
    """Count new cards in a deck."""
    return (
        db.session.query(Card)
        .filter(and_(Card.deck_id == deck_id, Card.state == 0))
        .count()
    )


def count_due_cards(deck_id) -> int:
    """Count cards due for review today in a deck."""
    today_end = get_today_end()

    return (
        db.session.query(Card)
        .filter(
            and_(
                Card.deck_id == deck_id,
                Card.due <= today_end,
                Card.state.in_([1, 2, 3]),  # Learning, Review, Relearning
            )
        )
        .count()
    )


def count_total_cards(deck_id: int) -> int:
    """Count total cards in a deck."""
    return db.session.query(Card).filter(Card.deck_id == deck_id).count()


def get_deck_stats(deck_id: int) -> dict:
    """
    Get statistics for a deck (new cards, due cards, etc.).

    Args:
        deck_id: The ID of the deck to analyze

    Returns:
        Dictionary with deck statistics
    """
    return {
        "new": count_new_cards(deck_id),
        "due": count_due_cards(deck_id),
        "total": count_total_cards(deck_id),
    }


def create_deck_stats_dict(deck: Deck) -> dict:
    """Create a deck statistics dictionary from a Deck object."""
    stats = get_deck_stats(deck.id)
    return {
        "id": deck.id,
        "name": deck.name,
        "new": stats["new"],
        "due": stats["due"],
        "total": stats["total"],
    }


def get_all_deck_stats() -> List[dict]:
    """
    Get statistics for all decks.

    Returns:
        List of dictionaries with deck info and statistics
    """
    decks = db.session.query(Deck).all()
    return [create_deck_stats_dict(deck) for deck in decks]


def get_deck_by_id(deck_id: int) -> Optional[Deck]:
    """
    Get a deck by its ID.

    Args:
        deck_id: The ID of the deck to retrieve

    Returns:
        Deck object or None if not found
    """
    return db.session.query(Deck).filter(Deck.id == deck_id).first()


def create_deck(name: str, **kwargs) -> Deck:
    """
    Create a new deck.

    Args:
        name: Name of the deck
        **kwargs: Additional deck parameters (FSRS settings)

    Returns:
        Created Deck object
    """
    deck = Deck(name=name, **kwargs)
    db.session.add(deck)
    db.session.commit()
    return deck


def get_all_decks() -> List[Deck]:
    """
    Get all decks.

    Returns:
        List of all Deck objects
    """
    return db.session.query(Deck).order_by(Deck.name).all()


def create_card(file_path, deck_id, copy=True):
    """
    Create a new card from a file.

    Args:
        file_path: Path to the source file
        deck_id: ID of the deck to add the card to
        copy: Whether to copy the file (default True)

    Returns:
        Created Card object

    """
    source_path = Path(file_path)
    if not source_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    deck = get_deck_by_id(deck_id)
    if not deck:
        raise ValueError(f"Deck not found: {deck_id}")

    if copy:
        # Read file data and write to managed store
        try:
            data = source_path.read_bytes()
        except Exception as e:
            raise IOError(f"Failed to read file: {e}")

        final_path = write_to_managed_store(data, deck.name, str(source_path))
    else:
        # Use original path
        final_path = str(source_path)

    # Get filesystem metadata
    final_path_obj = Path(final_path)
    stat_info = final_path_obj.stat()

    # Get device and inode info
    fs_dev = str(stat_info.st_dev)
    fs_inode = str(stat_info.st_ino)

    # Create card with defaults
    card = Card(
        deck_id=deck_id,
        path=final_path,
        fs_dev=fs_dev,
        fs_inode=fs_inode,
        is_external=not copy,
    )

    db.session.add(card)
    db.session.commit()

    return card
