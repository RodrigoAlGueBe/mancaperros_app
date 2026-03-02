from .auth import router as auth_router
from .users import router as users_router
from .exercises import router as exercises_router
from .routines import router as routines_router

__all__ = ["auth_router", "users_router", "exercises_router", "routines_router"]
