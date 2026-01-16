"""
Exercise Global model definition.

This module defines the Exercise_global SQLAlchemy model for global
exercise templates.
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from infrastructure.database.models.base import Base


class Exercise_global(Base):
    """
    Global Exercise model representing exercise templates.

    Global exercises are part of global routines and serve as
    templates for user-specific exercises.

    Attributes:
        exercise_id: Primary key identifier
        exercise_name: Name of the exercise
        rep: Repetitions or duration (as string for flexibility)
        exercise_type: Type classification (e.g., push, pull, isometric)
        exercise_group: Muscle group targeted
        rutine_id: Foreign key to parent global routine
        image: Path to exercise demonstration image

    Relationships:
        exercise_owner: Parent global routine
    """
    __tablename__ = "exercises_global"

    exercise_id = Column(Integer, primary_key=True, index=True)
    exercise_name = Column(
        String(255),
        nullable=False,
        unique=False,
        index=True,
        default="New exercise name"
    )
    rep = Column(
        String(255),
        nullable=False,
        unique=False,
        index=True,
        default="empty"
    )
    exercise_type = Column(
        String(255),
        nullable=False,
        unique=False,
        index=True,
        default="New exercise type"
    )
    exercise_group = Column(
        String(255),
        nullable=False,
        unique=False,
        index=True,
        default="New exercise group"
    )
    rutine_id = Column(
        Integer,
        ForeignKey("rutines_global.rutine_id"),
        nullable=False
    )
    image = Column(
        String(255),
        nullable=False,
        unique=False,
        index=True,
        default="empty"
    )

    # Relationships
    exercise_owner = relationship("Rutine_global", back_populates="exercises")
