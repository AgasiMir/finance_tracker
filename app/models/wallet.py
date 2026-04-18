from typing import TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import ForeignKey, String, Numeric, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


if TYPE_CHECKING:
    from app.models import Operation, User


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(127), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    balance: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0.0,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    operations: Mapped[list["Operation"]] = relationship(back_populates="wallet")
    user: Mapped["User"] = relationship(back_populates="wallets")

    __table_args__ = (
        CheckConstraint("balance >= 0.0", name="positive_balance_check"),
        UniqueConstraint("user_id", "name", name="unique_wallet_for_user"),
    )
