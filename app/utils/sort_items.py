from enum import Enum


class Sort(Enum):
    id = "created_at"
    amount = "amount"
    wallet_name = "wallet_name"
    description = "description"


class Direction(Enum):
    asc = "ASC"
    desc = "DESC"
