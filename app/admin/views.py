from sqladmin import ModelView

from app.models.operation import Operation
from app.models.user import User
from app.models.wallet import Wallet

from app.auth import hash_password


class UserAdmin(ModelView, model=User):
    # Permissions
    can_create = True
    can_delete = False
    # Metadata
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"
    # List page
    column_list = [User.id, User.email]
    column_searchable_list = [User.email]
    column_sortable_list = [User.email]
    # Details page
    column_details_exclude_list = [User.hashed_password]
    # Pagination options
    page_size = 10
    page_size_options = [10, 20, 50]
    # Form options
    column_labels = {"hashed_password": "password"}
    form_edit_rules = ["is_active", "role"]
    form_create_rules = ["email", "hashed_password", "role"]

    async def on_model_change(self, data, model, is_created, request) -> None:
        if is_created:
            # Hash the password before saving into DB !
            data["hashed_password"] = hash_password(data["hashed_password"])


class WalletAdmin(ModelView, model=Wallet):
    # Permissions
    can_create = True
    can_delete = False
    can_edit = False
    # Metadata
    category = "Средства"
    name = "Кошелек"
    name_plural = "Кошелеки"
    icon = "fa-solid fa-wallet"
    # List page
    column_list = ["user.email", Wallet.name, Wallet.balance]
    column_searchable_list = [Wallet.name]
    column_sortable_list = ["user.email", Wallet.balance, Wallet.name]
    # Pagination options
    page_size = 10
    page_size_options = [10, 20, 50]
    # Form options
    form_excluded_columns = ["operations"]


class OperationAdmin(ModelView, model=Operation):
    # Permissions
    can_create = False
    can_delete = False
    can_edit = False
    # Metadata
    category = "Средства"
    name = "Операция"
    name_plural = "Операции"
    icon = "fa-solid fa-exchange"
    # List page
    def date_format(value):
        return value.strftime("%d.%m.%Y")

    column_list = [
        Operation.wallet_name,
        Operation.description,
        Operation.amount,
        Operation.type,
    ]
    column_sortable_list = [Operation.type, Operation.amount, Operation.created_at]
    column_type_formatters = dict(
        ModelView.column_type_formatters, created_at=date_format
    )
    column_formatters = {Operation.description: lambda m, a: m.description[:20] + "..."}
    # Pagination options
    page_size = 10
    page_size_options = [10, 20, 50]
