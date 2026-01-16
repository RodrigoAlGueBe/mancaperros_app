"""
Base Repository implementation with generic CRUD operations.

This module provides a generic repository pattern implementation
that can be extended by specific domain repositories.
"""

from typing import TypeVar, Generic, Type, Sequence, Any

from sqlalchemy.orm import Session
from sqlalchemy import select

from infrastructure.database.session import Base


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic base repository with common CRUD operations.

    This class provides standard database operations that can be
    inherited by specific domain repositories.

    Type Parameters:
        ModelType: The SQLAlchemy model class
        CreateSchemaType: The Pydantic schema for creation
        UpdateSchemaType: The Pydantic schema for updates

    Attributes:
        model: The SQLAlchemy model class for this repository
        db: The database session
    """

    def __init__(self, model: Type[ModelType], db: Session) -> None:
        """
        Initialize the repository with a model and database session.

        Args:
            model: The SQLAlchemy model class
            db: The database session
        """
        self.model = model
        self.db = db

    def get_by_id(self, id: int, id_field: str = "id") -> ModelType | None:
        """
        Retrieve a single record by its ID.

        Args:
            id: The primary key value
            id_field: The name of the ID field (default: "id")

        Returns:
            The model instance if found, None otherwise
        """
        return self.db.query(self.model).filter(
            getattr(self.model, id_field) == id
        ).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """
        Retrieve all records with pagination.

        Args:
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return

        Returns:
            List of model instances
        """
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj_in: CreateSchemaType | dict[str, Any]) -> ModelType:
        """
        Create a new record in the database.

        Args:
            obj_in: The creation schema or dictionary with field values

        Returns:
            The created model instance
        """
        if isinstance(obj_in, dict):
            obj_data = obj_in
        else:
            obj_data = obj_in.dict() if hasattr(obj_in, "dict") else obj_in.model_dump()

        db_obj = self.model(**obj_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db_obj: ModelType,
        obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        """
        Update an existing record.

        Args:
            db_obj: The existing model instance to update
            obj_in: The update schema or dictionary with new values

        Returns:
            The updated model instance
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True) if hasattr(obj_in, "dict") else obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: int, id_field: str = "id") -> bool:
        """
        Delete a record by its ID.

        Args:
            id: The primary key value
            id_field: The name of the ID field (default: "id")

        Returns:
            True if the record was deleted, False if not found
        """
        obj = self.get_by_id(id, id_field)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False

    def delete_obj(self, db_obj: ModelType) -> bool:
        """
        Delete a specific model instance.

        Args:
            db_obj: The model instance to delete

        Returns:
            True after successful deletion
        """
        self.db.delete(db_obj)
        self.db.commit()
        return True

    def exists(self, id: int, id_field: str = "id") -> bool:
        """
        Check if a record with the given ID exists.

        Args:
            id: The primary key value
            id_field: The name of the ID field (default: "id")

        Returns:
            True if the record exists, False otherwise
        """
        return self.get_by_id(id, id_field) is not None

    def count(self) -> int:
        """
        Count total records in the table.

        Returns:
            Total number of records
        """
        return self.db.query(self.model).count()

    def flush(self) -> None:
        """
        Flush pending changes to the database without committing.

        Useful for getting auto-generated IDs before commit.
        """
        self.db.flush()

    def commit(self) -> None:
        """
        Commit the current transaction.
        """
        self.db.commit()

    def rollback(self) -> None:
        """
        Rollback the current transaction.
        """
        self.db.rollback()
