from typing import TYPE_CHECKING
from enum import Enum
from sqlalchemy import String, Boolean, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


if TYPE_CHECKING:
    from app.models import Wallet


class UserRole(Enum):
    user = "user"
    admin = "admin"


class User(Base):
    """Модель пользователя системы управления финансами.

    Атрибуты:
        id (int): Уникальный идентификатор пользователя (первичный ключ)
        email (str): Электронная почта пользователя (уникальная, до 255 символов)
        hashed_password (str): Хешированный пароль пользователя (до 255 символов)
        is_active (bool): Флаг активности пользователя, по умолчанию True
        role (UserRole): Роль пользователя (по умолчанию UserRole.user)
        wallets (list[Wallet]): Список кошельков, принадлежащих пользователю

    Ограничения:
        - Email должен быть уникальным для каждого пользователя
        - Пользователь может иметь несколько кошельков
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, native_enum=True),
        server_default="user",
        nullable=False,
    )

    wallets: Mapped[list["Wallet"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return self.email
