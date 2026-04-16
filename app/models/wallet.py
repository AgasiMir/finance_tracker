from decimal import Decimal
from sqlalchemy import String, Numeric, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Wallet(Base):
    __tablename__ = "wallets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(127), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    balance: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=0.0
    )

    __table_args__ = (CheckConstraint("balance >= 0.0", name="positive_balance_check"),)
