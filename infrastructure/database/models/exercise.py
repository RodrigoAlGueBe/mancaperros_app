"""
Exercise model definition.

This module defines the Exercise SQLAlchemy model for user-specific exercises.
"""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from infrastructure.database.models.base import Base
from infrastructure.database.models.soft_delete_mixin import SoftDeleteMixin


class Exercise(Base, SoftDeleteMixin):
    """
    Exercise model representing an individual exercise within a routine.

    Attributes:
        exercise_id: Primary key identifier
        exercise_name: Name of the exercise
        rep: Repetitions or duration (as string for flexibility)
        exercise_type: Type classification (e.g., push, pull, isometric)
        exercise_group: Muscle group targeted
        rutine_id: Foreign key to parent routine
        image: Path to exercise demonstration image

    Relationships:
        exercise_owner: Parent routine
    """
    __tablename__ = "exercises"

    exercise_id = Column(Integer, unique=True, index=True, primary_key=True)
    exercise_name = Column(
        String(255),
        unique=False,
        index=True,
        default="New exercise name"
    )
    rep = Column(String(255), unique=False, index=True, default="empty")
    exercise_type = Column(
        String(255),
        unique=False,
        index=True,
        default="New exercise type"
    )
    exercise_group = Column(
        String(255),
        unique=False,
        index=True,
        default="New exercise group"
    )
    rutine_id = Column(Integer, ForeignKey("rutines.rutine_id"))
    image = Column(String(255), unique=False, index=True, default="empty")

    # Relationships
    exercise_owner = relationship("Rutine", back_populates="exercises")
