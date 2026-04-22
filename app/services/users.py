import jwt
from app.config import settings
from app.schemas import UserCreate, UserPublic
from app.exceptions.python_exceptions import (
    CredentialsException,
)
from app.uow.uow import DBManager


class UserService:
    """Сервис для работы с пользователями.

    Содержит базовые методы для регистрации, входа
    и обновления токенов.
    """

    def __init__(self, user_repo: DBManager):
        """Инициализирует сервис пользователей.

        Args:
            user_repo (DBManager): Репозиторий для работы с пользователями.
        """

        self.user_repo = user_repo

    async def create_user(self, user: UserCreate) -> UserPublic:
        """Создает нового пользователя.

        Args:
            user (UserCreate): Данные для создания пользователя.

        Returns:
            UserPublic: Созданный пользователь.
        """

        return await self.user_repo.users.create_user(user)

    async def login(self, username: str, password: str) -> dict:
        """Аутентифицирует пользователя.

        Args:
            username (str): Email пользователя.
            password (str): Пароль пользователя.

        Returns:
            dict: Токены доступа.
        """

        return await self.user_repo.users.login_user(username, password)

    async def refresh_token(self, refresh_token: str):
        """Обновляет access token по refresh token.

        Args:
            refresh_token (str): Токен для обновления.

        Returns:
            dict: Новый access token.
        """

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

        if not await self.user_repo.users.get_user_by_email(email):
            raise CredentialsException

        return await self.user_repo.users.refresh_token(email)
