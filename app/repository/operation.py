from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Wallet, Operation
from app.schemas import OperationCreate, OperationsHistory, TransferMoneyCreate
from app.exceptions.python_exceptions import (
    InsufficientFundsException,
    SameWalletException,
    WalletNotFoundException,
)


class OperationRepository:
    """
    Репозиторий для операций с кошельками.

    Предоставляет методы для работы с финансовыми операциями:
    пополнение, снятие, перевод средств, а также получение истории операций.
    """

    def __init__(self, db: AsyncSession):
        """
        Инициализирует репозиторий операций.

        Args:
            db: Асинхронная сессия SQLAlchemy для работы с базой данных.
        """
        self.db = db

    @staticmethod
    def _from_db(model: Operation) -> OperationsHistory:
        """
        Преобразует модель Operation в схему OperationsHistory.

        Args:
            model: Экземпляр модели Operation из базы данных.

        Returns:
            OperationsHistory: Валидированная схема операции.
        """
        return OperationsHistory.model_validate(model)

    async def _get_wallet(self, wallet_name: str, user_id) -> Wallet:
        """
        Получает кошелек с блокировкой FOR UPDATE.
        Используется только в контексте операций изменения баланса.
        """
        return await self.db.scalar(
            select(Wallet)
            .where(
                Wallet.name == wallet_name,
                Wallet.user_id == user_id,
            )
            .with_for_update()
        )

    async def get_all_operations(
        self,
        sort_param: str,
        dir: str,
        offset: int,
        limit: int,
        user_id: int,
        filter: str | None = None,
    ) -> list[OperationsHistory]:
        """
        Получает список операций с пагинацией, сортировкой и фильтрацией.

        Args:
            sort_param: Поле для сортировки (например, "amount", "created_at").
            dir: Направление сортировки ("asc" или "desc").
            offset: Смещение для пагинации.
            limit: Количество записей на странице.
            user_id: Идентификатор пользователя для фильтрации по владельцу кошелька.
            filter: Опциональный фильтр по типу операции (например, "income", "expense").

        Returns:
            list[OperationsHistory]: Список операций, преобразованных в схему.
        """

        filters = []

        try:
            sort_column = getattr(Operation, sort_param)
        except AttributeError:
            raise ValueError(f"Column {sort_param} does not exist")

        if dir == "desc":
            sort_column = desc(sort_column)

        if filter:
            filters.append(Operation.type == filter)

        operations = await self.db.scalars(
            select(Operation)
            .join(Wallet, Operation.wallet_id == Wallet.id)
            .where(*filters, Wallet.user_id == user_id)
            .order_by(sort_column)
            .limit(limit)
            .offset(offset)
        )
        return [self._from_db(obj) for obj in operations.all()]

    async def add_money(
        self,
        operation: OperationCreate,
        user_id: int,
        type: str = "income",
    ) -> dict:
        """
        Пополняет баланс кошелька.

        Создает операцию пополнения и увеличивает баланс кошелька на указанную сумму.
        Использует блокировку FOR UPDATE для предотвращения гонок.

        Args:
            operation: Схема с данными операции (название кошелька, сумма, описание).
            user_id: Идентификатор пользователя-владельца кошелька.
            type: Тип операции (по умолчанию "income").

        Returns:
            dict: Словарь с сообщением, описанием и новым балансом.

        Raises:
            WalletNotFoundException: Если кошелек с указанным именем не найден.
        """

        wallet = await self._get_wallet(operation.wallet_name, user_id)
        if not wallet:
            raise WalletNotFoundException(operation.wallet_name)

        db_operation = Operation(
            **operation.model_dump(), wallet_id=wallet.id, type=type
        )
        self.db.add(db_operation)

        wallet.balance += operation.amount

        return {
            "message": f"Wallet {operation.wallet_name!r} balance increased by {operation.amount}",
            "description": operation.description,
            "new_balance": wallet.balance,
            "wallet_user": wallet.user,
        }

    async def withdraw_money(
        self,
        operation: OperationCreate,
        user_id: int,
        type: str = "expense",
    ) -> dict:
        """
        Снимает деньги с кошелька.

        Создает операцию расхода и уменьшает баланс кошелька на указанную сумму.
        Использует блокировку FOR UPDATE для предотвращения гонок.
        Проверяет достаточность средств перед списанием.

        Args:
            operation: Схема с данными операции (название кошелька, сумма, описание).
            user_id: Идентификатор пользователя-владельца кошелька.
            type: Тип операции (по умолчанию "expense").

        Returns:
            dict: Словарь с сообщением, описанием и новым балансом.

        Raises:
            WalletNotFoundException: Если кошелек с указанным именем не найден.
            InsufficientFundsException: Если на балансе недостаточно средств.
        """

        wallet = await self._get_wallet(operation.wallet_name, user_id)
        if not wallet:
            raise WalletNotFoundException(operation.wallet_name)

        if wallet.balance < operation.amount:
            raise InsufficientFundsException(wallet.name, wallet.balance)

        db_operation = Operation(
            **operation.model_dump(), wallet_id=wallet.id, type=type
        )
        self.db.add(db_operation)

        wallet.balance -= operation.amount

        return {
            "message": f"Wallet {operation.wallet_name!r} balance decreased by {operation.amount}",
            "description": operation.description,
            "new_balance": wallet.balance,
            "wallet_user": wallet.user,
        }

    async def transfer_money(self, transfer: TransferMoneyCreate, user_id: int) -> dict:
        """
        Переводит деньги между кошельками одного пользователя.

        Обеспечивает атомарность перевода: списывает сумму с одного кошелька
        и зачисляет на другой. Использует блокировку FOR UPDATE для обоих кошельков
        для предотвращения гонок. Проверяет существование обоих кошельков,
        достаточность средств и предотвращает перевод на тот же кошелек.

        Args:
            transfer: Схема перевода (кошелек-отправитель, кошелек-получатель, сумма).
            user_id: Идентификатор пользователя-владельца обоих кошельков.

        Returns:
            dict: Словарь с информацией о зачислении и списании.

        Raises:
            WalletNotFoundException: Если один из кошельков не найден.
            SameWalletException: Если попытка перевода на тот же кошелек.
            InsufficientFundsException: Если на балансе отправителя недостаточно средств.
        """

        wallet_from = await self._get_wallet(transfer.wallet_from, user_id)

        if not wallet_from:
            raise WalletNotFoundException(transfer.wallet_from)

        wallet_to = await self._get_wallet(transfer.wallet_to, user_id)

        if not wallet_to:
            raise WalletNotFoundException(transfer.wallet_to)

        if wallet_from.name == wallet_to.name:
            raise SameWalletException

        if wallet_from.balance < transfer.amount:
            raise InsufficientFundsException(
                transfer.wallet_from,
                wallet_from.balance,
            )

        wallet_from.balance -= transfer.amount
        wallet_to.balance += transfer.amount

        return {
            "add": f"Wallet {transfer.wallet_to!r} + {transfer.amount} = {wallet_to.balance}",
            "withdraw": f"Wallet {transfer.wallet_from!r} - {transfer.amount} = {wallet_from.balance}",
        }
