from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, ConfigDict, EmailStr


class WalletPublic(BaseModel):
    id: int
    name: str
    balance: float
    description: str

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
    type: str

    model_config = ConfigDict(from_attributes=True)


class TransferMoneyCreate(BaseModel):
    wallet_from: str
    wallet_to: str
    amount: Decimal

    @field_validator("amount")
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v


class TransferMoneyPublic(BaseModel):
    add: str
    withdraw: str


class UserCreate(BaseModel):
    email: EmailStr = Field(max_length=255, description="Email пользователя")
    password: str = Field(
        min_length=8,
        max_length=255,
        description="Пароль (минимум 8 символов, максимум - 255)",
    )


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
