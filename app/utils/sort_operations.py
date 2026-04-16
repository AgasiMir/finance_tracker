from enum import Enum


class Sort(Enum):
    # Using 'id' for sorting instead of 'created_at' to leverage primary key index
    # This works because id is auto-incremented and correlates with creation time
    id = "created_at"
    amount = "amount"
    wallet_name = "wallet_name"
    description = "description"


class Direction(Enum):
    desc = "DESC"
    asc = "ASC"
