# Soft Delete Architecture

## Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Application Layer                             │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              Service Layer (e.g., UserService)              │ │
│  │  - delete_user(user_id) -> uses soft_delete()               │ │
│  │  - restore_user(user_id) -> uses restore()                  │ │
│  └────────────────────┬────────────────────────────────────────┘ │
└─────────────────────────┼────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Repository Layer                                │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              BaseRepository (Generic)                        │ │
│  │                                                               │ │
│  │  Query Methods:                                              │ │
│  │  - get_by_id(id, include_deleted=False)                     │ │
│  │  - get_all(include_deleted=False)                           │ │
│  │  - get_by_field(field, value, include_deleted=False)        │ │
│  │                                                               │ │
│  │  Soft Delete Methods:                                        │ │
│  │  - soft_delete(obj) -> marks as deleted                     │ │
│  │  - soft_delete_by_id(id) -> finds & marks deleted           │ │
│  │  - soft_delete_by_field(field, value) -> marks multiple     │ │
│  │                                                               │ │
│  │  Restore Methods:                                            │ │
│  │  - restore(obj) -> unmarks as deleted                       │ │
│  │  - restore_by_id(id) -> finds & unmarks                     │ │
│  │                                                               │ │
│  │  Query Deleted Methods:                                      │ │
│  │  - get_deleted() -> only deleted records                    │ │
│  │  - get_deleted_by_field(field, value)                       │ │
│  │  - count_deleted() -> count of deleted                      │ │
│  │  - count_active() -> count of non-deleted                   │ │
│  │                                                               │ │
│  │  Helper Methods:                                             │ │
│  │  - _supports_soft_delete() -> check if model supports       │ │
│  │  - _apply_soft_delete_filter(query) -> filter out deleted   │ │
│  └──────────────────────┬──────────────────────────────────────┘ │
│                         │                                         │
│  ┌──────────────────────▼──────────────────────────────────────┐ │
│  │    Specific Repositories (e.g., UserRepository)             │ │
│  │    - Inherit from BaseRepository                            │ │
│  │    - Add domain-specific queries                            │ │
│  └──────────────────────┬──────────────────────────────────────┘ │
└─────────────────────────┼────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Model/ORM Layer                                   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              SoftDeleteMixin                                │ │
│  │                                                               │ │
│  │  Attributes:                                                 │ │
│  │  + deleted_at: Optional[datetime] = None                    │ │
│  │  + is_deleted: bool = False                                 │ │
│  │                                                               │ │
│  │  Methods:                                                    │ │
│  │  + soft_delete() -> sets is_deleted=True, deleted_at=now()  │ │
│  │  + restore() -> sets is_deleted=False, deleted_at=None      │ │
│  │  + is_soft_deleted() -> bool                                │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                         ▲                                         │
│                         │ (inherited by)                          │
│     ┌───────┬───────┬───┴───┬───────────┐                        │
│     │       │       │       │           │                        │
│  ┌──▼──┐ ┌──▼──────┐ ┌──▼──────┐ ┌──▼──────┐                    │
│  │User │ │Exercise │ │ Routine │ │Exercise │                    │
│  │     │ │  Plan   │ │ (Rutine)│ │          │                    │
│  └─────┘ └─────────┘ └─────────┘ └──────────┘                    │
│                                                                   │
│  All models inherit SoftDeleteMixin for consistent behavior       │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Database Layer                                   │
│                                                                   │
│  Example User Table:                                              │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ users                                                        │ │
│  ├────────┬──────────┬──────────┬──────────┬────────┬─────────┤ │
│  │user_id │user_name │  email   │...other..│is_del  │deleted_ │ │
│  │(PK)    │          │          │  fields  │eted   │at (IX)  │ │
│  ├────────┼──────────┼──────────┼──────────┼────────┼─────────┤ │
│  │ 1      │  alice   │alice@... │   ...    │ False  │ NULL    │ │
│  │ 2      │  bob     │bob@...   │   ...    │ True   │2024-... │ │ <- Soft-deleted
│  │ 3      │  charlie │charlie@..│   ...    │ False  │ NULL    │ │
│  └────────┴──────────┴──────────┴──────────┴────────┴─────────┘ │
│                                                                   │
│  Indexes on is_deleted and deleted_at for query performance     │
└─────────────────────────────────────────────────────────────────┘
```

## Behavior Flow

### Soft Delete Operation

```
User Request: delete_user(user_id=2)
              │
              ▼
    Service Layer
    - Calls repo.soft_delete_by_id(2)
              │
              ▼
    Repository Layer
    - Finds user (include_deleted=False, so finds active user)
    - Calls user.soft_delete() [from Mixin]
    - Commits to database
              │
              ▼
    Model Layer (SoftDeleteMixin)
    - user.is_deleted = True
    - user.deleted_at = datetime.utcnow()
              │
              ▼
    Database
    - Updates: is_deleted=True, deleted_at='2024-01-15 10:30:45'
    - Data remains in database (not deleted)
```

### Query with Soft Delete Filter

```
Query: repo.get_all()
       │
       ▼
   BaseRepository.get_all()
   - Creates query: SELECT * FROM users
   - Calls _apply_soft_delete_filter()
       │
       ▼
   _apply_soft_delete_filter(query)
   - Checks _supports_soft_delete() -> True
   - Adds filter: WHERE is_deleted = FALSE
       │
       ▼
   Database
   - Returns only non-deleted records
   - User bob (is_deleted=True) is excluded
```

### Restore Operation

```
Admin: restore_user(user_id=2)
       │
       ▼
   Repository.restore_by_id(2)
   - Finds user with include_deleted=True
   - Calls user.restore() [from Mixin]
   - Commits to database
       │
       ▼
   Model Layer (SoftDeleteMixin)
   - user.is_deleted = False
   - user.deleted_at = None
       │
       ▼
   Database
   - Updates: is_deleted=False, deleted_at=NULL
   - User appears in normal queries again
```

## Data State Lifecycle

```
┌─────────────┐
│   Created   │  is_deleted=False, deleted_at=NULL
└──────┬──────┘
       │ soft_delete()
       ▼
┌─────────────────────────┐
│   Soft Deleted          │  is_deleted=True, deleted_at='2024-01-15 10:30:45'
│   (Recoverable)         │
└──────┬──────────────────┘
       │ restore()
       ▼
┌─────────────┐
│   Restored  │  is_deleted=False, deleted_at=NULL
└─────────────┘
       │ hard_delete() [future]
       ▼
┌─────────────────────────┐
│   Hard Deleted          │  Record completely removed from database
│   (Non-recoverable)     │
└─────────────────────────┘
```

## Query Pattern Examples

### Pattern 1: Exclude Deleted (Default)

```
Active Users Only

SQL:
SELECT * FROM users
WHERE is_deleted = FALSE
ORDER BY created_at DESC

Repository:
users = repo.get_all()  # include_deleted defaults to False
```

### Pattern 2: Include Deleted (For Admin)

```
All Users (including deleted)

SQL:
SELECT * FROM users
ORDER BY created_at DESC

Repository:
users = repo.get_all(include_deleted=True)
```

### Pattern 3: Only Deleted (Recovery)

```
Deleted Users Only

SQL:
SELECT * FROM users
WHERE is_deleted = TRUE
ORDER BY deleted_at DESC

Repository:
deleted = repo.get_deleted()
```

### Pattern 4: Soft Delete Multiple

```
Archive inactive users

Python:
deleted_count = repo.soft_delete_by_field('status', 'inactive')

SQL (happens in loop):
UPDATE users
SET is_deleted = TRUE, deleted_at = NOW()
WHERE status = 'inactive'
```

## Performance Considerations

### Indexes

```sql
-- Index on is_deleted for quick filtering
CREATE INDEX ix_users_is_deleted ON users(is_deleted);

-- Index on deleted_at for audit/recovery
CREATE INDEX ix_users_deleted_at ON users(deleted_at);

-- Compound index for efficient queries
CREATE INDEX ix_users_soft_delete ON users(is_deleted, deleted_at);
```

### Query Performance

```
Query Type              │ Index Used          │ Performance
────────────────────────┼─────────────────────┼────────────
get_all()               │ ix_is_deleted       │ O(log n)
get_deleted()           │ ix_is_deleted       │ O(log n)
restore_by_id()         │ PRIMARY (user_id)   │ O(1)
count_active()          │ ix_is_deleted       │ O(log n)
```

## Implementation Checklist

### Phase 1: Infrastructure (DONE)

- [x] Create SoftDeleteMixin with deleted_at and is_deleted fields
- [x] Add soft_delete() and restore() methods to mixin
- [x] Update BaseRepository with soft delete methods
- [x] Add _supports_soft_delete() detection
- [x] Add _apply_soft_delete_filter() to queries
- [x] Update User model to inherit SoftDeleteMixin
- [x] Update Exercise_plan model to inherit SoftDeleteMixin
- [x] Update Rutine model to inherit SoftDeleteMixin
- [x] Update Exercise model to inherit SoftDeleteMixin

### Phase 2: Database Migration (TODO)

- [ ] Create Alembic migration to add columns
- [ ] Run migration on development database
- [ ] Test migration up/down
- [ ] Deploy migration to staging/production

### Phase 3: Application Logic (TODO)

- [ ] Update services to use soft_delete() instead of hard delete()
- [ ] Update API endpoints to support soft delete behavior
- [ ] Add soft delete filtering to all repository queries
- [ ] Update views/responses to handle soft deleted data

### Phase 4: Cascade Rule Updates (TODO)

- [ ] Change cascade="all, delete-orphan" to cascade="all"
- [ ] Test relationship behavior
- [ ] Verify soft-deleted children aren't included in parent loads

### Phase 5: Admin Interface (TODO)

- [ ] Add UI to view deleted records
- [ ] Add UI to restore deleted records
- [ ] Add audit logging for soft deletes
- [ ] Add deletion history view

### Phase 6: Monitoring & Maintenance (TODO)

- [ ] Add metrics for soft delete operations
- [ ] Create purge job for old deleted records (if needed)
- [ ] Add alerts for unexpected deletions
- [ ] Regular audits of deleted data

## Related Models Structure

```
User (soft deletable)
  ├── exercise_plan (soft deletable) [cascade="all, delete-orphan"]
  │     ├── rutines (soft deletable) [cascade="all, delete-orphan"]
  │     │     └── exercises (soft deletable) [cascade="all, delete-orphan"]
  │     └── routine_group_order (JSON)
  ├── exercise_plan_global
  ├── user_tracker (legacy)
  └── workout_events [cascade="all, delete-orphan"]

Current Behavior:
- Hard delete User -> hard deletes exercise_plan, rutines, exercises
- Hard delete exercise_plan -> hard deletes rutines, exercises

With Soft Delete (after Phase 4):
- Soft delete User -> marks user as deleted, child records remain
- Hard delete User -> cascades hard delete to children
```
