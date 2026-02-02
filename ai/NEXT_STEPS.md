# Soft Delete Implementation - Next Steps

## Phase 2: Database Migration (READY TO EXECUTE)

### Step 1: Create Alembic Migration

```bash
cd C:\Users\Rodrigo\Desktop\proyectos\mancaperros_app\code\backend\mancaperros_app

# Option A: Autogenerate migration (recommended)
alembic revision --autogenerate -m "Add soft delete columns to main models"

# Option B: Manual migration (if autogenerate doesn't detect columns)
# Copy MIGRATION_SOFT_DELETE_TEMPLATE.py to alembic/versions/
# Rename and adjust the down_revision value
```

### Step 2: Verify Migration File

The generated migration file (in `alembic/versions/`) should contain:

```python
def upgrade() -> None:
    # Add columns to users
    op.add_column('users', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('is_deleted', sa.Boolean(), server_default='false'))
    op.create_index('ix_users_deleted_at', 'users', ['deleted_at'])
    op.create_index('ix_users_is_deleted', 'users', ['is_deleted'])

    # Add columns to exercise_plans
    op.add_column('exercise_plans', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.add_column('exercise_plans', sa.Column('is_deleted', sa.Boolean(), server_default='false'))
    op.create_index('ix_exercise_plans_deleted_at', 'exercise_plans', ['deleted_at'])
    op.create_index('ix_exercise_plans_is_deleted', 'exercise_plans', ['is_deleted'])

    # Add columns to rutines
    op.add_column('rutines', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.add_column('rutines', sa.Column('is_deleted', sa.Boolean(), server_default='false'))
    op.create_index('ix_rutines_deleted_at', 'rutines', ['deleted_at'])
    op.create_index('ix_rutines_is_deleted', 'rutines', ['is_deleted'])

    # Add columns to exercises
    op.add_column('exercises', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    op.add_column('exercises', sa.Column('is_deleted', sa.Boolean(), server_default='false'))
    op.create_index('ix_exercises_deleted_at', 'exercises', ['deleted_at'])
    op.create_index('ix_exercises_is_deleted', 'exercises', ['is_deleted'])
```

### Step 3: Test Migration on Development Database

```bash
# Create a backup of development database first
cp database.db database.db.backup

# Upgrade to latest migration
alembic upgrade head

# Verify tables have new columns
alembic current  # Shows current head

# Test downgrade (rollback)
alembic downgrade -1

# Upgrade again
alembic upgrade head
```

### Step 4: Verify Schema in Database

```python
# Quick Python script to verify columns exist
from sqlalchemy import create_engine, inspect

engine = create_engine('sqlite:///./database.db')  # Adjust connection string
inspector = inspect(engine)

# Check users table
columns = inspector.get_columns('users')
column_names = [col['name'] for col in columns]
print(f"User columns: {column_names}")

# Verify soft delete columns exist
assert 'is_deleted' in column_names, "is_deleted column missing"
assert 'deleted_at' in column_names, "deleted_at column missing"
print("✓ Soft delete columns verified")
```

### Step 5: Deployment

```bash
# Test environment
alembic upgrade head
python -m pytest tests/  # Run all tests

# Staging environment
# - Run migration
# - Run smoke tests
# - Verify data integrity

# Production environment
# - Create database backup
# - Run migration during maintenance window
# - Monitor for errors
# - Verify application works
```

## Phase 3: Application Integration (NEXT)

### Update Service Layer

Update each service to use soft delete:

```python
# File: app/services/user_service.py

from app.infrastructure.database.repositories.user_repository import UserRepository

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def delete_user(self, user_id: int) -> bool:
        """
        Soft delete a user instead of hard delete.

        This preserves user data for recovery and audit purposes.
        """
        user = self.repo.get_by_id(user_id, id_field="user_id")
        if not user:
            return False

        return self.repo.soft_delete(user)

    def restore_user(self, user_id: int) -> bool:
        """Restore a soft-deleted user."""
        return self.repo.restore_by_id(user_id, id_field="user_id")

    def list_users(self, skip: int = 0, limit: int = 100):
        """List only active (non-deleted) users."""
        return self.repo.get_all(skip=skip, limit=limit, include_deleted=False)

    def list_deleted_users(self, skip: int = 0, limit: int = 100):
        """List deleted users (admin function)."""
        return self.repo.get_deleted(skip=skip, limit=limit)
```

### Update API Endpoints

```python
# File: app/api/users.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user_schema import UserResponse, UserListResponse
from app.services.user_service import UserService
from app.infrastructure.database.repositories.user_repository import UserRepository
from app.database import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)) -> dict:
    """
    Soft delete a user.

    The user data is preserved in the database but marked as deleted.
    Only administrators can access deleted users.
    """
    repo = UserRepository(db)
    service = UserService(repo)

    if not service.delete_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User deleted successfully", "user_id": user_id}


@router.post("/{user_id}/restore")
def restore_user(user_id: int, db: Session = Depends(get_db)) -> dict:
    """
    Restore a soft-deleted user.

    Only administrators can restore deleted users.
    """
    repo = UserRepository(db)
    service = UserService(repo)

    if not service.restore_user(user_id):
        raise HTTPException(
            status_code=404,
            detail="User not found or is already active"
        )

    return {"message": "User restored successfully", "user_id": user_id}


@router.get("/admin/deleted")
def list_deleted_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> UserListResponse:
    """
    Get all deleted users.

    Admin only endpoint for viewing and recovering deleted users.
    """
    repo = UserRepository(db)
    service = UserService(repo)

    deleted_users = service.list_deleted_users(skip=skip, limit=limit)

    return UserListResponse(
        data=deleted_users,
        total=repo.count_deleted(),
        skip=skip,
        limit=limit
    )
```

### Update Repositories

```python
# File: app/infrastructure/database/repositories/user_repository.py

from app.infrastructure.database.repositories.base_repository import BaseRepository
from infrastructure.database.models.user import User

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """User repository with soft delete support."""

    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str, include_deleted: bool = False) -> Optional[User]:
        """Get user by email, excluding deleted by default."""
        return self.get_by_field("email", email, include_deleted=include_deleted)

    # Soft delete methods are inherited from BaseRepository
    # No additional implementation needed
```

### Update Tests

```python
# File: tests/test_user_service.py

import pytest
from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app.infrastructure.database.repositories.user_repository import UserRepository
from infrastructure.database.models.user import User

@pytest.fixture
def user_service(db: Session):
    repo = UserRepository(db)
    return UserService(repo)

def test_delete_user_soft_deletes(user_service, db: Session):
    """Test that delete_user() performs soft delete."""
    # Create user
    user = User(user_name="test", email="test@example.com")
    db.add(user)
    db.commit()
    user_id = user.user_id

    # Delete user
    success = user_service.delete_user(user_id)
    assert success == True

    # Verify soft deleted
    repo = UserRepository(db)
    user = repo.get_by_id(user_id, id_field="user_id", include_deleted=True)
    assert user.is_deleted == True
    assert user.deleted_at is not None

def test_restore_user(user_service, db: Session):
    """Test that restore_user() restores soft-deleted user."""
    # Create and delete user
    user = User(user_name="test", email="test@example.com")
    db.add(user)
    db.commit()
    user_id = user.user_id

    user_service.delete_user(user_id)

    # Restore user
    success = user_service.restore_user(user_id)
    assert success == True

    # Verify restored
    repo = UserRepository(db)
    user = repo.get_by_id(user_id, id_field="user_id")
    assert user is not None
    assert user.is_deleted == False

def test_list_users_excludes_deleted(user_service, db: Session):
    """Test that list_users() excludes deleted users."""
    # Create users
    user1 = User(user_name="active", email="active@example.com")
    user2 = User(user_name="deleted", email="deleted@example.com")
    db.add_all([user1, user2])
    db.commit()

    user_service.delete_user(user2.user_id)

    # List users
    users = user_service.list_users()

    assert len(users) == 1
    assert users[0].user_name == "active"
```

## Phase 4: Cascade Rules Update (AFTER Phase 3)

### Before Running This Phase

Ensure Phase 3 is complete and all applications are using `soft_delete()` instead of `delete()`.

### Update Models

```python
# File: infrastructure/database/models/user.py

class User(Base, SoftDeleteMixin):
    # ... existing fields ...

    # BEFORE:
    # exercise_plan = relationship(
    #     "Exercise_plan",
    #     back_populates="exercise_plan_owner",
    #     cascade="all, delete-orphan"  # Permanent deletion!
    # )

    # AFTER:
    exercise_plan = relationship(
        "Exercise_plan",
        back_populates="exercise_plan_owner",
        cascade="all"  # Allow soft delete to cascade
    )
```

### Verify Cascade Behavior

```python
def test_cascade_soft_delete():
    """Verify cascade behavior with soft delete."""
    user = User(user_name="test", email="test@example.com")
    plan = Exercise_plan(exercise_plan_name="Test Plan")
    routine = Rutine(rutine_name="Test Routine")
    exercise = Exercise(exercise_name="Test Exercise")

    user.exercise_plan.append(plan)
    plan.rutines.append(routine)
    routine.exercises.append(exercise)

    db.add(user)
    db.commit()

    # Soft delete user
    repo.soft_delete(user)

    # Verify cascade: all children marked as deleted
    assert user.is_deleted == True
    assert plan.is_deleted == True
    assert routine.is_deleted == True
    assert exercise.is_deleted == True
```

## Phase 5: Admin Interface (FUTURE)

### Create Admin Views

```python
# File: app/api/admin/users.py

@router.get("/admin/users/deleted")
def view_deleted_users(db: Session = Depends(get_db)):
    """Admin endpoint to view all deleted users."""
    repo = UserRepository(db)
    deleted = repo.get_deleted()
    return {"deleted_users": deleted}

@router.post("/admin/users/{user_id}/restore")
def admin_restore_user(user_id: int, db: Session = Depends(get_db)):
    """Admin endpoint to restore deleted user."""
    repo = UserRepository(db)
    success = repo.restore_by_id(user_id, id_field="user_id")
    if success:
        return {"message": "User restored"}
    raise HTTPException(status_code=404, detail="User not found")

@router.get("/admin/stats/deleted")
def view_deletion_stats(db: Session = Depends(get_db)):
    """Admin endpoint for deletion statistics."""
    user_repo = UserRepository(db)
    return {
        "total_users": user_repo.count() + user_repo.count_deleted(),
        "active_users": user_repo.count_active(),
        "deleted_users": user_repo.count_deleted(),
        "deletion_rate": user_repo.count_deleted() / max(user_repo.count_active(), 1)
    }
```

## Phase 6: Monitoring & Maintenance (ONGOING)

### Add Metrics

```python
# File: app/monitoring/metrics.py

from prometheus_client import Counter, Gauge

soft_delete_counter = Counter(
    'soft_delete_total',
    'Total soft deletes',
    ['entity_type']
)

restore_counter = Counter(
    'soft_delete_restore_total',
    'Total restores',
    ['entity_type']
)

deleted_records_gauge = Gauge(
    'soft_delete_deleted_count',
    'Number of deleted records',
    ['entity_type']
)

# Usage in service
def delete_user(self, user_id: int):
    success = self.repo.soft_delete(user)
    if success:
        soft_delete_counter.labels(entity_type='user').inc()
        deleted_records_gauge.labels(entity_type='user').set(
            self.repo.count_deleted()
        )
    return success
```

### Create Purge Job (Optional)

```python
# File: app/tasks/purge_old_deleted.py

from datetime import datetime, timedelta
from app.infrastructure.database.repositories.user_repository import UserRepository

async def purge_deleted_records(days_to_keep: int = 90):
    """
    Permanently delete records soft-deleted more than N days ago.

    This is optional and should only run if you don't need archived data.
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)

    repo = UserRepository(db)

    # Find records to purge
    old_deleted = db.query(User).filter(
        User.is_deleted == True,
        User.deleted_at < cutoff_date
    ).all()

    # Permanently delete (hard delete)
    for record in old_deleted:
        db.delete(record)

    db.commit()
    return len(old_deleted)
```

## Quick Reference

### Database Migration
```bash
alembic revision --autogenerate -m "Add soft delete columns"
alembic upgrade head
```

### Testing
```bash
pytest tests/test_soft_delete_example.py -v
pytest tests/test_user_service.py -v
```

### Verify Implementation
```python
# Check soft delete is working
user = User(user_name="test", email="test@example.com")
db.add(user)
db.commit()

# Soft delete
repo.soft_delete(user)

# Verify
assert user.is_deleted == True
assert user.deleted_at is not None
```

## Timeline Estimate

- Phase 2 (Migration): 1-2 hours
- Phase 3 (Integration): 4-8 hours
- Phase 4 (Cascade): 2-4 hours
- Phase 5 (Admin UI): 8-16 hours
- Phase 6 (Monitoring): 4-8 hours

**Total**: 2-4 weeks for full implementation

## Support

For issues or questions:
1. Check SOFT_DELETE_IMPLEMENTATION.md for detailed docs
2. Review SOFT_DELETE_ARCHITECTURE.md for diagrams
3. Run example tests: `pytest tests/test_soft_delete_example.py`
4. Check test file for usage examples

---

**Next Action**: Run Phase 2 database migration
