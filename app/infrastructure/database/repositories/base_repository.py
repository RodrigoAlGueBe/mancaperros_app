"""
Base Repository - Abstract base class for all repositories.

This module implements the Repository Pattern to abstract data access logic,
providing a clean separation between domain logic and data persistence.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import and_

# Generic type for the model
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Abstract base repository that defines the interface for data access operations.

    This class implements common CRUD operations and can be extended by specific
    repositories to add domain-specific queries.

    Type Parameters:
        ModelType: The SQLAlchemy model class
        CreateSchemaType: The Pydantic schema for creating entities
        UpdateSchemaType: The Pydantic schema for updating entities

    Attributes:
        model: The SQLAlchemy model class this repository manages
        db: The database session
    """

    def __init__(self, model: Type[ModelType], db: Session):
        """
        Initialize the repository with a model class and database session.

        Args:
            model: The SQLAlchemy model class
            db: The database session
        """
        self.model = model
        self.db = db

    def _supports_soft_delete(self) -> bool:
        """
        Check if the model supports soft delete functionality.

        A model supports soft delete if it has both 'is_deleted' and 'deleted_at' columns.

        Returns:
            True if the model has soft delete fields, False otherwise
        """
        return hasattr(self.model, "is_deleted") and hasattr(self.model, "deleted_at")

    def _apply_soft_delete_filter(self, query):
        """
        Apply soft delete filter to exclude deleted records.

        If the model supports soft delete, filters out records where is_deleted=True.

        Args:
            query: The SQLAlchemy query object

        Returns:
            The filtered query (or unchanged if model doesn't support soft delete)
        """
        if self._supports_soft_delete():
            return query.filter(self.model.is_deleted == False)
        return query

    def get_by_id(self, id: int, id_field: str = "id", include_deleted: bool = False) -> Optional[ModelType]:
        """
        Retrieve an entity by its primary key.

        Args:
            id: The primary key value
            id_field: The name of the primary key field (default: "id")
            include_deleted: If True, includes soft-deleted records (default: False)

        Returns:
            The entity if found, None otherwise
        """
        query = self.db.query(self.model).filter(
            getattr(self.model, id_field) == id
        )
        if not include_deleted:
            query = self._apply_soft_delete_filter(query)
        return query.first()

    def get_all(self, skip: int = 0, limit: int = 100, include_deleted: bool = False) -> List[ModelType]:
        """
        Retrieve all entities with pagination.

        By default, soft-deleted records are excluded. Pass include_deleted=True to include them.

        Args:
            skip: Number of records to skip (offset)
            limit: Maximum number of records to return
            include_deleted: If True, includes soft-deleted records (default: False)

        Returns:
            List of entities
        """
        query = self.db.query(self.model)
        if not include_deleted:
            query = self._apply_soft_delete_filter(query)
        return query.offset(skip).limit(limit).all()

    def get_by_field(self, field_name: str, value: Any, include_deleted: bool = False) -> Optional[ModelType]:
        """
        Retrieve a single entity by a specific field value.

        Args:
            field_name: The name of the field to filter by
            value: The value to match
            include_deleted: If True, includes soft-deleted records (default: False)

        Returns:
            The first entity matching the criteria, or None
        """
        query = self.db.query(self.model).filter(
            getattr(self.model, field_name) == value
        )
        if not include_deleted:
            query = self._apply_soft_delete_filter(query)
        return query.first()

    def get_all_by_field(
        self,
        field_name: str,
        value: Any,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False
    ) -> List[ModelType]:
        """
        Retrieve all entities matching a specific field value.

        Args:
            field_name: The name of the field to filter by
            value: The value to match
            skip: Number of records to skip
            limit: Maximum number of records to return
            include_deleted: If True, includes soft-deleted records (default: False)

        Returns:
            List of entities matching the criteria
        """
        query = self.db.query(self.model).filter(
            getattr(self.model, field_name) == value
        )
        if not include_deleted:
            query = self._apply_soft_delete_filter(query)
        return query.offset(skip).limit(limit).all()

    def create(self, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new entity from a Pydantic schema.

        Args:
            obj_in: The Pydantic schema with creation data

        Returns:
            The created entity
        """
        if hasattr(obj_in, "dict"):
            obj_in_data = obj_in.dict() if callable(obj_in.dict) else obj_in.dict
        elif hasattr(obj_in, "model_dump"):
            obj_in_data = obj_in.model_dump()
        else:
            obj_in_data = dict(obj_in)

        db_obj = self.model(**obj_in_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def create_from_dict(self, data: Dict[str, Any]) -> ModelType:
        """
        Create a new entity from a dictionary.

        Args:
            data: Dictionary with entity data

        Returns:
            The created entity
        """
        db_obj = self.model(**data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def create_without_commit(self, data: Dict[str, Any]) -> ModelType:
        """
        Create a new entity without committing the transaction.
        Useful for batch operations or when the caller manages the transaction.

        Args:
            data: Dictionary with entity data

        Returns:
            The created entity (not yet committed)
        """
        db_obj = self.model(**data)
        self.db.add(db_obj)
        self.db.flush()  # Get the ID without committing
        return db_obj

    def update(self, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        """
        Update an existing entity with data from a Pydantic schema.

        Args:
            db_obj: The existing database entity
            obj_in: The Pydantic schema with update data

        Returns:
            The updated entity
        """
        if hasattr(obj_in, "dict"):
            obj_data = obj_in.dict(exclude_unset=True) if callable(obj_in.dict) else obj_in.dict
        elif hasattr(obj_in, "model_dump"):
            obj_data = obj_in.model_dump(exclude_unset=True)
        else:
            obj_data = dict(obj_in)

        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update_from_dict(self, db_obj: ModelType, data: Dict[str, Any]) -> ModelType:
        """
        Update an existing entity with data from a dictionary.

        Args:
            db_obj: The existing database entity
            data: Dictionary with update data

        Returns:
            The updated entity
        """
        for field, value in data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, db_obj: ModelType) -> bool:
        """
        Delete an entity.

        Args:
            db_obj: The entity to delete

        Returns:
            True if deletion was successful
        """
        self.db.delete(db_obj)
        self.db.commit()
        return True

    def delete_by_id(self, id: int, id_field: str = "id") -> bool:
        """
        Delete an entity by its primary key.

        Args:
            id: The primary key value
            id_field: The name of the primary key field

        Returns:
            True if an entity was deleted, False if not found
        """
        deleted_count = self.db.query(self.model).filter(
            getattr(self.model, id_field) == id
        ).delete()
        self.db.commit()
        return deleted_count > 0

    def delete_by_field(self, field_name: str, value: Any) -> int:
        """
        Delete all entities matching a field value.

        Args:
            field_name: The name of the field to filter by
            value: The value to match

        Returns:
            Number of deleted entities
        """
        deleted_count = self.db.query(self.model).filter(
            getattr(self.model, field_name) == value
        ).delete()
        self.db.commit()
        return deleted_count

    def exists(self, id: int, id_field: str = "id") -> bool:
        """
        Check if an entity exists by its primary key.

        Args:
            id: The primary key value
            id_field: The name of the primary key field

        Returns:
            True if the entity exists, False otherwise
        """
        return self.db.query(self.model).filter(
            getattr(self.model, id_field) == id
        ).first() is not None

    def exists_by_field(self, field_name: str, value: Any) -> bool:
        """
        Check if an entity exists by a field value.

        Args:
            field_name: The name of the field to check
            value: The value to match

        Returns:
            True if an entity exists with that field value
        """
        return self.db.query(self.model).filter(
            getattr(self.model, field_name) == value
        ).first() is not None

    def count(self) -> int:
        """
        Count all entities.

        Returns:
            Total number of entities
        """
        return self.db.query(self.model).count()

    def count_by_field(self, field_name: str, value: Any) -> int:
        """
        Count entities matching a field value.

        Args:
            field_name: The name of the field to filter by
            value: The value to match

        Returns:
            Number of matching entities
        """
        return self.db.query(self.model).filter(
            getattr(self.model, field_name) == value
        ).count()

    def commit(self) -> None:
        """Commit the current transaction."""
        self.db.commit()

    def rollback(self) -> None:
        """Rollback the current transaction."""
        self.db.rollback()

    def refresh(self, db_obj: ModelType) -> ModelType:
        """
        Refresh an entity from the database.

        Args:
            db_obj: The entity to refresh

        Returns:
            The refreshed entity
        """
        self.db.refresh(db_obj)
        return db_obj

    def soft_delete(self, db_obj: ModelType) -> bool:
        """
        Soft delete an entity by marking it as deleted.

        If the model supports soft delete, marks the entity with is_deleted=True
        and sets deleted_at timestamp. Otherwise, performs a hard delete.

        Args:
            db_obj: The entity to delete

        Returns:
            True if soft delete was successful, False if model doesn't support soft delete

        Raises:
            Exception: If the database operation fails
        """
        if not self._supports_soft_delete():
            return False

        db_obj.soft_delete()  # Calls the mixin method
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return True

    def soft_delete_by_id(self, id: int, id_field: str = "id") -> bool:
        """
        Soft delete an entity by its primary key.

        Args:
            id: The primary key value
            id_field: The name of the primary key field

        Returns:
            True if soft delete was successful, False if not found or doesn't support soft delete
        """
        if not self._supports_soft_delete():
            return False

        db_obj = self.get_by_id(id, id_field, include_deleted=False)
        if not db_obj:
            return False

        return self.soft_delete(db_obj)

    def soft_delete_by_field(self, field_name: str, value: Any) -> int:
        """
        Soft delete all entities matching a field value.

        Args:
            field_name: The name of the field to filter by
            value: The value to match

        Returns:
            Number of soft-deleted entities
        """
        if not self._supports_soft_delete():
            return 0

        db_objects = self.get_all_by_field(field_name, value, skip=0, limit=999999, include_deleted=False)
        count = 0
        for db_obj in db_objects:
            if self.soft_delete(db_obj):
                count += 1
        return count

    def restore(self, db_obj: ModelType) -> bool:
        """
        Restore a soft-deleted entity.

        If the model supports soft delete, marks the entity with is_deleted=False
        and clears the deleted_at timestamp.

        Args:
            db_obj: The soft-deleted entity to restore

        Returns:
            True if restore was successful, False if model doesn't support soft delete
        """
        if not self._supports_soft_delete():
            return False

        db_obj.restore()  # Calls the mixin method
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return True

    def restore_by_id(self, id: int, id_field: str = "id") -> bool:
        """
        Restore a soft-deleted entity by its primary key.

        Args:
            id: The primary key value
            id_field: The name of the primary key field

        Returns:
            True if restore was successful, False if not found or doesn't support soft delete
        """
        if not self._supports_soft_delete():
            return False

        # Must include deleted records to find and restore them
        db_obj = self.get_by_id(id, id_field, include_deleted=True)
        if not db_obj or not db_obj.is_soft_deleted():
            return False

        return self.restore(db_obj)

    def get_deleted(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Retrieve all soft-deleted entities.

        Only works if the model supports soft delete.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of soft-deleted entities, or empty list if model doesn't support soft delete
        """
        if not self._supports_soft_delete():
            return []

        return self.db.query(self.model).filter(
            self.model.is_deleted == True
        ).offset(skip).limit(limit).all()

    def get_deleted_by_field(self, field_name: str, value: Any, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Retrieve soft-deleted entities matching a field value.

        Args:
            field_name: The name of the field to filter by
            value: The value to match
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of soft-deleted entities matching criteria
        """
        if not self._supports_soft_delete():
            return []

        return self.db.query(self.model).filter(
            and_(
                getattr(self.model, field_name) == value,
                self.model.is_deleted == True
            )
        ).offset(skip).limit(limit).all()

    def count_deleted(self) -> int:
        """
        Count all soft-deleted entities.

        Returns:
            Number of soft-deleted entities, or 0 if model doesn't support soft delete
        """
        if not self._supports_soft_delete():
            return 0

        return self.db.query(self.model).filter(
            self.model.is_deleted == True
        ).count()

    def count_active(self) -> int:
        """
        Count all non-deleted (active) entities.

        Returns:
            Number of active entities
        """
        if self._supports_soft_delete():
            return self.db.query(self.model).filter(
                self.model.is_deleted == False
            ).count()
        return self.db.query(self.model).count()
