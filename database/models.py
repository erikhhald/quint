from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Deck(Base):
    __tablename__ = "decks"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # FSRS deck-level parameters (can be customized per deck)
    w = Column(
        Text,
        default="[0.4, 0.6, 2.4, 5.8, 4.93, 0.94, 0.86, 0.01, 1.49, 0.14, 0.94, 2.18, 0.05, 0.34, 1.26, 0.29, 2.61]",
    )  # FSRS weights as JSON string
    request_retention = Column(Float, default=0.9)  # Desired retention rate
    maximum_interval = Column(Integer, default=36500)  # Maximum interval in days
    enable_fuzz = Column(Integer, default=1)  # Enable/disable fuzzing (0 or 1)


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True)
    deck_id = Column(Integer, nullable=False)
    front = Column(Text, nullable=False)
    back = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # FSRS core scheduling parameters
    due = Column(DateTime, default=datetime.utcnow)  # When the card is due for review
    stability = Column(Float, default=0.0)  # Memory stability (S)
    difficulty = Column(Float, default=0.0)  # Memory difficulty (D)
    elapsed_days = Column(Integer, default=0)  # Days since last review
    scheduled_days = Column(Integer, default=0)  # Scheduled interval
    reps = Column(Integer, default=0)  # Number of reviews
    lapses = Column(Integer, default=0)  # Number of lapses (forgetting events)
    state = Column(
        Integer, default=0
    )  # Card state: 0=New, 1=Learning, 2=Review, 3=Relearning
    last_review = Column(DateTime)  # Timestamp of last review


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True)
    deck_id = Column(Integer, nullable=False)
    message = Column(Text, nullable=False)
    response = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

