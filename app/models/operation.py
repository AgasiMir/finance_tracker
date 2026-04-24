from typing import TYPE_CHECKING
from decimal import Decimal
from datetime import datetime
from sqlalchemy import String, DateTime, Numeric, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.core.database import Base


if TYPE_CHECKING:
    from app.models import Wallet


class Operation(Base):
    """Модель операции для отслеживания финансовых транзакций.

    Атрибуты:
        id (int): Уникальный идентификатор операции (первичный ключ)
        wallet_name (str): Название кошелька, к которому привязана операция (до 127 символов)
        description (str | None): Описание операции (до 255 символов, опционально)
        amount (Decimal): Сумма операции (до 10 цифр, 2 после запятой), индексируется
        type (str): Тип операции (до 7 символов), индексируется
        created_at (datetime): Дата и время создания операции, устанавливается автоматически
        wallet_id (int): Идентификатор кошелька, к которому привязана операция
        wallet (Wallet): Ссылка на кошелек, к которому привязана операция

    Ограничения:
        - Сумма операции должна быть положительной (> 0.0)
        - При удалении кошелька операция не может быть удалена (ограничение RESTRICT)
    """

    __tablename__ = "operations"

    id: Mapped[int] = mapped_column(primary_key=True)
    wallet_name: Mapped[str] = mapped_column(
        String(127),
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        index=True,
    )
    type: Mapped[str] = mapped_column(
        String(7),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )

    wallet_id: Mapped[int] = mapped_column(
        ForeignKey("wallets.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    wallet: Mapped["Wallet"] = relationship(back_populates="operations")

    __table_args__ = (CheckConstraint("amount > 0.0", name="positive_amount_check"),)

    def __repr__(self) -> str:
        return f"Operation(wallet_name={self.wallet_name}, amount={self.amount}, type={self.type}, created_at={self.created_at})"
