from sqlalchemy.orm import Session

import crud
import models
import schemas


class UserService:

    @staticmethod
    def create_user(db: Session, user: schemas.User_Create) -> models.User:
        if db.query(models.User).filter(models.User.email == user.email).first():
            raise ValueError("Email already registered")

        if db.query(models.User).filter(models.User.user_name == user.user_name).first():
            raise ValueError("Username already exist")

        db_user = crud.create_user(db=db, user=user)
        if not db_user:
            raise RuntimeError("Error in user creation, user have not been created")

        return db_user

    @staticmethod
    def get_current_user_info(db: Session, email: str) -> models.User:
        user = crud.get_user_by_email(db=db, user_email=email)
        if not user:
            raise ValueError("Email not registered")
        return user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> models.User:
        user = crud.get_user_by_email(db, user_email=email)
        if not user:
            raise ValueError("User not found")
        return user

    @staticmethod
    def get_all_users(db: Session) -> list[models.User]:
        users = crud.get_users(db=db)
        if not users:
            raise ValueError("Not users in aplication registered yet")
        return users

    @staticmethod
    def get_main_page_info(db: Session, email: str) -> dict:
        user = crud.get_user_by_email(db, user_email=email)
        if not user:
            raise ValueError("User not found")

        exercise_plan = db.query(models.Exercise_plan).filter(
            models.Exercise_plan.user_owner_id == user.user_id
        ).first()

        return {
            "user_name": user.user_name,
            "email": user.email,
            "user_image": user.user_image,
            "exercise_plan_name": exercise_plan.exercise_plan_name if exercise_plan else None,
            "exercise_plan_id": exercise_plan.exercise_plan_id if exercise_plan else None,
        }
