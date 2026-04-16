from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, ConfigDict


class WalletPublic(BaseModel):
    id: int
    name: str
    balance: float
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class WalletCreate(BaseModel):
    name: str = Field(max_length=127)
    description: str | None = Field(default=None, max_length=255)

    @field_validator("name")
    def wallet_name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if len(v) <= 0:
            raise ValueError("Wallet name cannot be empty")
        return v


class OperationPublic(BaseModel):
    message: str
    description: str
    new_balance: float


class OperationCreate(BaseModel):
    wallet_name: str = Field(max_length=127)
    amount: Decimal
    description: str | None = Field(default=None, max_length=255)

    @field_validator("amount")
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v


class OperationsHistory(BaseModel):
    id: int
    wallet_name: str
    amount: float
    created_at: datetime
    description: str

    model_config = ConfigDict(from_attributes=True)
