from typing import TYPE_CHECKING
from decimal import Decimal
from datetime import datetime
from sqlalchemy import String, DateTime, Numeric, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.core.database import Base


if TYPE_CHECKING:
    from app.models import Wallet


class Operation(Base):
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
