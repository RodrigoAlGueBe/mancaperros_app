"""
Soft Delete Mixin - Reusable mixin for soft delete functionality.

This module provides a mixin class that can be inherited by SQLAlchemy models
to implement soft delete functionality. Instead of permanently deleting records,
soft delete marks them as deleted using a timestamp and boolean flag.

This approach allows for:
- Data recovery
- Historical auditing
- Compliance with data retention policies
- Preserving referential integrity during migrations
"""

from datetime import datetime, UTC

from sqlalchemy import Column, DateTime, Boolean
from sqlalchemy.orm import declared_attr


class SoftDeleteMixin:
    """
    Mixin class that adds soft delete functionality to SQLAlchemy models.

    When a model inherits from this mixin, it gains soft delete capabilities.
    Instead of being permanently removed from the database, records are marked
    as deleted using a timestamp and boolean flag.

    Attributes:
        deleted_at: Timestamp of when the record was soft-deleted (NULL if not deleted)
        is_deleted: Boolean flag for quick filtering of deleted records (default: False)

    Usage:
        class User(Base, SoftDeleteMixin):
            __tablename__ = "users"
            user_id = Column(Integer, primary_key=True)
            # ... other fields ...

        # In repository:
        user = repo.soft_delete(user_obj)  # Marks user as deleted
        users = repo.get_all()  # Only returns non-deleted users by default
    """

    @declared_attr
    def deleted_at(cls):
        return Column(
            DateTime,
            nullable=True,
            index=True,
            default=None,
            doc="Timestamp when the record was soft-deleted"
        )

    @declared_attr
    def is_deleted(cls):
        return Column(
            Boolean,
            default=False,
            index=True,
            doc="Boolean flag for quick filtering of deleted records"
        )

    def soft_delete(self) -> None:
        """
        Mark this record as deleted without removing it from the database.

        Sets the is_deleted flag to True and records the deletion timestamp.
        This method should be called through the repository to ensure
        database consistency.
        """
        self.is_deleted = True
        self.deleted_at = datetime.now(UTC)

    def restore(self) -> None:
        """
        Restore a soft-deleted record.

        Clears the is_deleted flag and deleted_at timestamp.
        This method should be called through the repository to ensure
        database consistency.
        """
        self.is_deleted = False
        self.deleted_at = None

    def is_soft_deleted(self) -> bool:
        """
        Check if this record has been soft-deleted.

        Returns:
            True if the record is marked as deleted, False otherwise
        """
        return self.is_deleted is True and self.deleted_at is not None
