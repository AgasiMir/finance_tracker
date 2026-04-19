from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions.python_exceptions import (
    IncorrectCredentialsException,
    UserAlreadyExistsException,
)
from app.models import User
from app.schemas import UserCreate, UserPublic
from app.auth import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    def _from_db(model: User) -> UserPublic:
        return UserPublic.model_validate(model)

    async def get_user_by_email(self, email: str) -> User:
        return await self.db.scalar(select(User).where(User.email == email))

    async def create_user(self, user: UserCreate) -> UserPublic:
        if await self.get_user_by_email(user.email):
            raise UserAlreadyExistsException

        db_user = User(
            email=user.email,
            hashed_password=hash_password(user.password),
        )

        self.db.add(db_user)
        await self.db.flush()

        return self._from_db(db_user)

    async def login_user(self, username: str, password: str) -> dict:
        user = await self.get_user_by_email(username)

        if not user or not verify_password(password, user.hashed_password):
            raise IncorrectCredentialsException

        access_token = create_access_token(data={"sub": user.email, "id": user.id})
        refresh_token = create_refresh_token(data={"sub": user.email, "id": user.id})
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def refresh_token(self, email: str) -> dict:
        user = await self.get_user_by_email(email)

        access_token = create_access_token(
            data={
                "sub": user.email,
                "id": user.id,
            }
        )

        return {"access_token": access_token, "token_type": "bearer"}
