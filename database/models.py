from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import object_session, relationship

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
    created_at = Column(DateTime, default=datetime.utcnow)

    # File system tracking
    path = Column(String(500), nullable=False)  # Filepath to the card content
    fs_dev = Column(Text)  # device id (or volume id)
    fs_inode = Column(Text)  # inode or file index
    is_external = Column(Boolean, default=False)

    # FSRS core scheduling parameters
    due = Column(DateTime, default=datetime.utcnow)  # When the card is due for review
    stability = Column(Float, default=0.0)  # Memory stability (S)
    difficulty = Column(Float, default=0.0)  # Memory difficulty (D)
    elapsed_days = Column(Integer, default=0)  # Days since last review
    scheduled_days = Column(Integer, default=0)  # Scheduled interval
    state = Column(
        Integer, default=0
    )  # Card state: 0=New, 1=Learning, 2=Review, 3=Relearning

    # anki scheduling parameters
    anki_difficulty = Column(Float, default=2.5)  # SM2 easiness factor (difficulty)

    # Relationships
    reviews = relationship("Review", back_populates="card")

    @property
    def reps(self):
        """Number of reviews for this card."""
        session = object_session(self)
        if session is None:
            return 0
        return (
            session.query(func.count(Review.id))
            .filter(Review.card_id == self.id)
            .scalar()
            or 0
        )

    @property
    def lapses(self):
        """Number of lapses (ratings of 0=Again) for this card."""
        session = object_session(self)
        if session is None:
            return 0
        return (
            session.query(func.count(Review.id))
            .filter(Review.card_id == self.id, Review.rating == 0)
            .scalar()
            or 0
        )

    @property
    def last_review(self):
        """Timestamp of the most recent review."""
        session = object_session(self)
        if session is None:
            return None
        latest_review = (
            session.query(Review.reviewed_at)
            .filter(Review.card_id == self.id)
            .order_by(Review.reviewed_at.desc())
            .first()
        )
        return latest_review[0] if latest_review else None


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)

    card_id = Column(Integer, ForeignKey("cards.id"), nullable=False, index=True)

    reviewed_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Rating / button pressed, e.g. 0=Again, 1=Hard, 2=Good, 3=Easy
    rating = Column(Integer, nullable=False)

    response_ms = Column(Integer)

    # Snapshot of scheduling state around the review
    state_before = Column(Integer)  # 0=New,1=Learning,2=Review,3=Relearning
    state_after = Column(Integer)

    scheduled_days_before = Column(Integer)
    scheduled_days_after = Column(Integer)

    elapsed_days = Column(Integer)  # days since last_review at the moment of answering

    stability_before = Column(Float)
    stability_after = Column(Float)
    difficulty_before = Column(Float)
    difficulty_after = Column(Float)

    # Which scheduler produced this review's decision ("fsrs", "sm2", "ebisu", etc.)
    algorithm = Column(String(32))

    # Relationships
    card = relationship("Card", back_populates="reviews")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    review_id = Column(Integer, nullable=False)
    message = Column(Text, nullable=False)
    response = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
