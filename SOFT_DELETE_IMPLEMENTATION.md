# Soft Delete Implementation - MED-09

## Overview

This document describes the soft delete implementation for the main models to prevent permanent data loss when deleting records. Instead of permanently removing data from the database, records are marked as deleted using a timestamp and boolean flag.

## Problem Statement

**MED-09**: Relations use `cascade="all, delete-orphan"` which permanently deletes data when parent records are deleted. This causes irreversible data loss and compliance issues.

## Solution Architecture

### 1. SoftDeleteMixin

Located at: `infrastructure/database/models/soft_delete_mixin.py`

A reusable mixin class that adds soft delete functionality to any SQLAlchemy model.

**Attributes:**
- `deleted_at: Optional[datetime]` - Timestamp of when the record was soft-deleted (NULL if not deleted)
- `is_deleted: bool = False` - Boolean flag for quick filtering of deleted records

**Methods:**
- `soft_delete()` - Marks record as deleted (sets is_deleted=True, deleted_at=now())
- `restore()` - Restores soft-deleted record (sets is_deleted=False, deleted_at=None)
- `is_soft_deleted()` - Checks if record has been soft-deleted

### 2. Modified Models

The following models now inherit from `SoftDeleteMixin`:

#### User Model
- File: `infrastructure/database/models/user.py`
- Changes: `class User(Base, SoftDeleteMixin):`
- Impact: User deletion is now soft (preserves data integrity)

#### Exercise_plan Model
- File: `infrastructure/database/models/exercise_plan.py`
- Changes: `class Exercise_plan(Base, SoftDeleteMixin):`
- Impact: Exercise plans can be restored if deleted by mistake

#### Rutine (Routine) Model
- File: `infrastructure/database/models/routine.py`
- Changes: `class Rutine(Base, SoftDeleteMixin):`
- Impact: Routines within plans are soft-deleted

#### Exercise Model
- File: `infrastructure/database/models/exercise.py`
- Changes: `class Exercise(Base, SoftDeleteMixin):`
- Impact: Individual exercises are soft-deleted

### 3. BaseRepository Enhancements

Located at: `app/infrastructure/database/repositories/base_repository.py`

#### Helper Methods

**_supports_soft_delete()** - Detects if a model has soft delete fields
```python
if repo._supports_soft_delete():
    # Model supports soft delete
```

**_apply_soft_delete_filter(query)** - Automatically excludes soft-deleted records from queries

#### Enhanced Query Methods

All query methods now support `include_deleted` parameter:

```python
# Get non-deleted user (default behavior)
user = repo.get_by_id(user_id)

# Include soft-deleted records if needed
all_users = repo.get_all(include_deleted=True)

# Get users by field, excluding deleted
users = repo.get_all_by_field("is_active", True)
```

Modified methods:
- `get_by_id(id, id_field="id", include_deleted=False)`
- `get_all(skip=0, limit=100, include_deleted=False)`
- `get_by_field(field_name, value, include_deleted=False)`
- `get_all_by_field(field_name, value, skip=0, limit=100, include_deleted=False)`

#### Soft Delete Operations

**Soft Delete:**
```python
# Soft delete single entity
success = repo.soft_delete(user_object)

# Soft delete by ID
success = repo.soft_delete_by_id(user_id, id_field="user_id")

# Soft delete multiple by field value
count = repo.soft_delete_by_field("status", "inactive")
```

**Restore:**
```python
# Restore soft-deleted entity
success = repo.restore(deleted_user_object)

# Restore by ID (must use include_deleted=True to find)
success = repo.restore_by_id(user_id, id_field="user_id")
```

**Query Deleted Records:**
```python
# Get all soft-deleted records
deleted_users = repo.get_deleted(skip=0, limit=100)

# Get deleted records by field
deleted = repo.get_deleted_by_field("status", "archived")

# Count deleted records
deleted_count = repo.count_deleted()

# Count active (non-deleted) records
active_count = repo.count_active()
```

## Database Migration Strategy

### Phase 1: Add Columns (Current)
Add `deleted_at` and `is_deleted` columns to tables:
- users
- exercise_plans
- rutines
- exercises

**Migration Example:**
```python
# alembic: auto migration
def upgrade():
    op.add_column('users', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('is_deleted', sa.Boolean(), server_default='false'))
    op.create_index(op.f('ix_users_deleted_at'), 'users', ['deleted_at'])
    op.create_index(op.f('ix_users_is_deleted'), 'users', ['is_deleted'])
```

### Phase 2: Update Cascade Rules (Future)
Remove or modify `cascade="all, delete-orphan"` to use cascade="all" instead.
This will preserve soft-deleted child records when parents are deleted.

### Phase 3: Application Logic Updates
Update services and repositories to use soft_delete() instead of hard delete().

## Usage Examples

### Repository Usage

```python
from app.infrastructure.database.repositories.user_repository import UserRepository

# Initialize
repo = UserRepository(db)

# Get active users (soft-deleted excluded)
active_users = repo.get_all()

# Include deleted in results
all_users = repo.get_all(include_deleted=True)

# Soft delete a user
user = repo.get_by_id(user_id)
if user:
    repo.soft_delete(user)

# Get all deleted users
deleted = repo.get_deleted()

# Restore a deleted user
success = repo.restore_by_id(user_id)
```

### Service Layer

```python
from app.services.user_service import UserService

service = UserService(repo)

# Delete operation now uses soft delete
service.delete_user(user_id)  # Soft deletes instead of hard delete

# Can restore
service.restore_user(user_id)
```

## Important Constraints

### Cascade Behavior

**IMPORTANT**: The cascade rules remain unchanged for now:
```python
# Still uses cascade="all, delete-orphan"
exercise_plan = relationship(
    "Exercise_plan",
    back_populates="exercise_plan_owner",
    cascade="all, delete-orphan"
)
```

This means when a User is hard-deleted, its Exercise_plans will also be hard-deleted.
The soft-delete implementation provides the mechanism; cascade rules will be updated in Phase 2.

### Deterministic Behavior

When a parent is deleted:
1. If using `repo.soft_delete(parent)` - Only parent is marked deleted
2. If using `repo.delete(parent)` - Cascade still applies (hard delete)
3. Soft-deleted children are excluded from queries automatically

## Backward Compatibility

- Existing `delete()` method still performs hard deletes
- Existing queries automatically exclude soft-deleted records
- The `include_deleted=True` parameter is optional for backward compatibility
- Models without soft delete support ignore all soft-delete operations gracefully

## Query Performance Considerations

### Indexes
The implementation creates indexes on:
- `is_deleted` - Fast filtering for active records
- `deleted_at` - Audit trail and purging operations

### Query Optimization
```python
# Efficient: Uses is_deleted index
active = repo.get_all()  # WHERE is_deleted = FALSE

# Efficient: Uses compound filter
deleted = repo.get_deleted()  # WHERE is_deleted = TRUE
```

## Data Recovery

Soft-deleted data remains in the database indefinitely (unless explicitly purged).

### Viewing Deleted Data
```python
# Get all deleted records
deleted_users = repo.get_deleted()

# Check deletion timestamp
for user in deleted_users:
    print(f"User {user.user_id} deleted at {user.deleted_at}")
```

### Recovery Window
No automatic purging is implemented. Data remains available for:
- Manual recovery
- Compliance auditing
- Historical analysis
- Legal holds

## Future Enhancements

1. **Purge Job** - Automatic deletion of soft-deleted records after N days
2. **Audit Logging** - Track who deleted what and when
3. **Restore UI** - Admin interface for restoring deleted data
4. **Hard Delete API** - Explicit method for permanent deletion
5. **Batch Operations** - Optimize bulk soft deletes

## Testing

### Unit Tests Structure
```python
# Test soft delete
assert user.is_deleted == False
repo.soft_delete(user)
assert user.is_deleted == True
assert user.deleted_at is not None

# Test filtering
active = repo.get_all()
assert len(active) == n  # Doesn't include deleted

deleted = repo.get_all(include_deleted=True)
assert len(deleted) > len(active)

# Test restore
repo.restore(user)
assert user.is_deleted == False
assert user.deleted_at is None
```

## Migration Checklist

- [ ] Run database migration to add columns
- [ ] Create integration tests for soft delete
- [ ] Update repository tests to verify filtering
- [ ] Update service layer tests
- [ ] Document soft delete in API documentation
- [ ] Update admin dashboard to show deleted records
- [ ] Create monitoring/alerts for soft delete events
- [ ] Train team on new soft delete behavior
- [ ] Plan Phase 2 cascade rule updates

## References

- **Soft Delete Pattern**: Industry standard for preserving data integrity
- **Cascade Strategies**: SQLAlchemy cascade documentation
- **Database Auditing**: Compliance and recovery patterns
