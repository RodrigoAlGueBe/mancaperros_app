from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated, List

router = APIRouter(
    prefix="/routines",
    tags=["Routines"],
)

# TODO: Move routine endpoints from main.py
# - POST /users/exercise_plans_global/routines_global
# - GET /exercise_plans/{exercise_plan_id}/rutines
# - GET /rutines/get_asigned_routines
# - GET /rutines/{rutine_id}/exercises
