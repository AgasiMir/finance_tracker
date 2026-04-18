import jwt
from app.config import settings
from app.auth import verify_password
from app.repository.user import UserRepository
from app.schemas import UserCreate, UserPublic
from app.exceptions.python_exceptions import (
    IncorrectCredentialsException,
    CredentialsException,
)


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def create_user(self, user: UserCreate) -> UserPublic:

        return await self.user_repo.create_user(user)

    async def login(self, username: str, password: str) -> dict:
        user = await self.user_repo.get_user_by_email(username)

        if not user or not verify_password(password, user.hashed_password):
            raise IncorrectCredentialsException

        return await self.user_repo.login_user(username)

    async def refresh_token(self, refresh_token: str):

        try:
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            email: str = payload.get("sub")
            token_type: str | None = payload.get("token_type")
            if email is None or token_type != "refresh":
                raise CredentialsException

        except jwt.ExpiredSignatureError:
            raise CredentialsException
        except jwt.PyJWTError:
            raise CredentialsException

        if not await self.user_repo.get_user_by_email(email):
            raise CredentialsException

        return await self.user_repo.refresh_token(email)
