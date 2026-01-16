# Mancaperros App - Test Suite

Comprehensive test suite for the Mancaperros FastAPI application covering authentication, user management, exercise plans, routines, and CRUD operations.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and test configuration
├── test_auth.py            # Authentication and token tests
├── test_users.py           # User endpoint tests
├── test_exercise_plans.py  # Exercise plan endpoint tests
├── test_routines.py        # Routine endpoint tests
├── test_crud.py           # CRUD operations tests
├── test_models.py         # Database model tests
└── README.md              # This file
```

## Test Coverage

### Authentication Tests (test_auth.py)
- User registration (success, duplicates, validation)
- Login with email/username
- Token generation and validation
- Token expiration handling
- Invalid token rejection
- Token signature verification

### User Tests (test_users.py)
- Get user by email
- Get all users
- Get current authenticated user
- User authorization checks
- User data validation
- Password hashing verification

### Exercise Plan Tests (test_exercise_plans.py)
- Create global exercise plans
- Assign plans to users
- Get available plans by type
- Plan replacement logic
- Full plan creation (with routines and exercises)
- Validation and error handling

### Routine Tests (test_routines.py)
- Create routines for exercise plans
- Get assigned routines
- Get routine exercises
- End routine with progress tracking
- Get next routine in sequence
- Routine validation

### CRUD Tests (test_crud.py)
- User CRUD operations
- Exercise plan CRUD operations
- Routine CRUD operations
- Exercise CRUD operations
- Password hashing and verification
- Authentication helpers
- User tracking operations

### Model Tests (test_models.py)
- Model creation and validation
- Model relationships (User → Plan → Routine → Exercise)
- Default values
- Cascade deletes
- Database constraints
- JSON field handling

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_auth.py
pytest tests/test_users.py
pytest tests/test_exercise_plans.py
pytest tests/test_routines.py
pytest tests/test_crud.py
pytest tests/test_models.py
```

### Run Specific Test Class
```bash
pytest tests/test_auth.py::TestUserRegistration
pytest tests/test_users.py::TestGetUserByEmail
```

### Run Specific Test Function
```bash
pytest tests/test_auth.py::TestUserRegistration::test_create_user_success
```

### Run with Verbose Output
```bash
pytest -v
```

### Run with Coverage Report
```bash
pytest --cov=. --cov-report=html
```

### Run Tests by Marker
```bash
pytest -m auth          # Run only authentication tests
pytest -m crud          # Run only CRUD tests
pytest -m "not slow"    # Skip slow tests
```

## Test Fixtures

All tests use shared fixtures defined in `conftest.py`:

### Database Fixtures
- `test_db`: In-memory SQLite database (function scope)
- `client`: FastAPI TestClient with database override

### User Fixtures
- `test_user`: Primary test user with known credentials
- `second_test_user`: Secondary user for authorization tests

### Authentication Fixtures
- `auth_token`: Valid JWT token for test_user
- `auth_headers`: Authorization headers with Bearer token
- `expired_token`: Expired JWT token for testing expiration
- `invalid_token`: Malformed token for validation tests

### Exercise Plan Fixtures
- `test_exercise_plan_global`: Pre-created global exercise plan

## Test Database

Tests use an **in-memory SQLite database** that is:
- Created fresh for each test
- Automatically cleaned up after each test
- Completely isolated (no test interference)
- Fast and doesn't require external database setup

## Best Practices

### Test Independence
All tests are independent and can run in any order. Each test:
- Creates its own test data
- Uses function-scoped fixtures
- Cleans up automatically

### Test Naming
Tests follow clear naming conventions:
- `test_<action>_<expected_result>`
- Example: `test_create_user_duplicate_email`

### Test Structure
Each test follows AAA pattern:
1. **Arrange**: Set up test data
2. **Act**: Execute the code under test
3. **Assert**: Verify the results

### Documentation
Every test includes:
- Clear docstring explaining what is tested
- "Validates that:" section listing specific checks
- Descriptive assertions

## Continuous Integration

These tests are designed to run in CI/CD pipelines:
- No external dependencies required
- Fast execution (in-memory database)
- Clear pass/fail indicators
- Detailed error messages

## Troubleshooting

### Import Errors
If you get import errors, make sure you're in the correct directory:
```bash
cd C:/Users/Rodrigo/Desktop/proyectos/mancaperros_app/code/backend/mancaperros_app
pytest
```

### Database Errors
If tests fail with database errors:
- Check that SQLAlchemy and dependencies are installed
- Verify `database.py` configuration is correct
- Ensure `conftest.py` is in the tests directory

### Token Errors
If authentication tests fail:
- Verify `config.py` settings are correct
- Check that `SECRET_KEY` is set
- Ensure `jose` library is installed

## Test Statistics

- **Total Test Files**: 6
- **Estimated Test Count**: 60+ individual tests
- **Coverage Areas**: Authentication, Users, Exercise Plans, Routines, CRUD, Models
- **Test Database**: SQLite in-memory
- **Execution Time**: < 5 seconds (typical)

## Adding New Tests

When adding new tests:

1. Use existing fixtures from `conftest.py`
2. Follow naming conventions
3. Add docstrings
4. Ensure test independence
5. Test both success and failure cases
6. Run all tests before committing

Example:
```python
def test_new_feature_success(self, client, auth_headers):
    """
    Test new feature works correctly.

    Validates that:
    - Feature performs expected action
    - Returns correct response
    """
    response = client.post("/new-endpoint", headers=auth_headers)
    assert response.status_code == 200
```

## Dependencies

Required packages for testing:
- pytest
- fastapi
- sqlalchemy
- pydantic
- python-jose[cryptography]
- passlib[bcrypt]
- pytest-cov (optional, for coverage)

Install with:
```bash
pip install pytest pytest-cov
```
