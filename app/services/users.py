from datetime import datetime, timedelta, timezone
import jwt
from app.config import settings
from app.email.send_email_async import send_email_async
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

        Notes:
            При успешном создании отправляет приветственное письмо на email пользователя.
        """

        res = await self.user_repo.users.create_user(user)
        if res:
            send_email_async.delay(
                user.email,
                "Регистрация на сайте",
                body=f"{user.email}!\n\nДобро пожаловать",
            )
            return res

    async def login(self, username: str, password: str, client_host: str) -> dict:
        """Аутентифицирует пользователя.

        Args:
            username (str): Email пользователя.
            password (str): Пароль пользователя.
            client_host (str): IP-адрес клиента для логирования входа.

        Returns:
            dict: Токены доступа.

        Notes:
            При успешной аутентификации отправляет уведомление на email пользователя
            с информацией о времени входа и IP-адресе.
        """

        res = await self.user_repo.users.login_user(username, password)

        if res:
            timezone_offset = +3.0
            tzinfo = timezone(timedelta(hours=timezone_offset))
            current_datetime = datetime.now(tzinfo)
            current_datetime = datetime.strftime(current_datetime, "%Y-%m-%d %H:%M:%S")

            user = await self.user_repo.users.get_user_by_email(username)

            send_email_async.delay(
                user.email,
                "Вход в систему",
                body=f"{user.email}. Был осуществлен вход в систему c IP {client_host}\n\nВремя входа: {current_datetime}",
            )
            return res

    async def refresh_token(self, refresh_token: str) -> dict:
        """Обновляет access token по refresh token.

        Args:
            refresh_token (str): Токен для обновления.

        Returns:
            dict: Новый access token.

        Raises:
            CredentialsException: Если токен невалиден, истек или пользователь не найден.
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
