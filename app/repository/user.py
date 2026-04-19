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
    """Репозиторий для работы с пользователями системы.

    Предоставляет методы для аутентификации, регистрации и управления
    пользователями в базе данных. Осуществляет все операции с пользовательскими
    данными, включая хранение хешированных паролей и выдачу токенов доступа.
    """

    def __init__(self, db: AsyncSession):
        """Инициализирует репозиторий с сессией базы данных.

        Args:
            db (AsyncSession): Асинхронная сессия SQLAlchemy для работы с БД.
        """
        self.db = db

    @staticmethod
    def _from_db(model: User) -> UserPublic:
        """Преобразует модель User в схему UserPublic.

        Args:
            model (User): Модель пользователя из базы данных.

        Returns:
            UserPublic: Валидированная схема для публичного представления пользователя.
        """
        return UserPublic.model_validate(model)

    async def get_user_by_email(self, email: str) -> User:
        """Получает пользователя по его email адресу.

        Args:
            email (str): Email адрес пользователя для поиска.

        Returns:
            User: Модель пользователя, если найден, иначе None.
        """
        return await self.db.scalar(select(User).where(User.email == email))

    async def create_user(self, user: UserCreate) -> UserPublic:
        """Создаёт нового пользователя в системе.

        Args:
            user (UserCreate): Данные для создания нового пользователя.

        Returns:
            UserPublic: Созданный пользователь в публичном представлении.

        Raises:
            UserAlreadyExistsException: Если пользователь с таким email уже существует.
        """
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
        """Аутентифицирует пользователя и выдаёт токены доступа.

        Args:
            username (str): Email пользователя (используется как имя пользователя).
            password (str): Пароль пользователя для проверки.

        Returns:
            dict: Словарь с access_token, refresh_token и типом токена.

        Raises:
            IncorrectCredentialsException: Если учетные данные неверны.
        """
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
        """Обновляет access token для пользователя по его email.

        Args:
            email (str): Email пользователя для обновления токена.

        Returns:
            dict: Словарь с новым access_token и типом токена.
        """
        user = await self.get_user_by_email(email)

        access_token = create_access_token(
            data={
                "sub": user.email,
                "id": user.id,
            }
        )

        return {"access_token": access_token, "token_type": "bearer"}
