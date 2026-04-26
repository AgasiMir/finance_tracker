from fastapi_cache import FastAPICache
from app.email.send_email_async import send_email_async
from app.schemas import OperationCreate, TransferMoneyCreate, OperationsHistory
from app.uow.uow import DBManager


class OperationService:
    """Сервис для управления операциями с деньгами.

    Предоставляет методы для получения истории операций, пополнения,
    снятия и перевода денег между кошельками.
    """

    def __init__(self, operation_repo: DBManager):
        """Инициализирует сервис операций.

        Args:
            operation_repo (DBManager): Менеджер базы данных для операций.
        """
        self.operation_repo = operation_repo

    async def get_all_operations(
        self,
        sort_param: str,
        dir: str,
        offset: int,
        limit: int,
        user_id: int,
        filter: str | None = None,
    ) -> list[OperationsHistory]:
        """Получает историю операций с пагинацией, сортировкой и фильтрацией.

        Args:
            sort_param (str): Поле для сортировки (например, "date", "amount").
            dir (str): Направление сортировки ("asc" или "desc").
            offset (int): Смещение для пагинации.
            limit (int): Количество записей на странице.
            user_id (int): Идентификатор пользователя.
            filter (str | None): Опциональный фильтр по типу операции.

        Returns:
            list[OperationsHistory]: Список операций, соответствующих критериям.
        """
        return await self.operation_repo.operations.get_all_operations(
            sort_param, dir, offset, limit, user_id, filter
        )

    async def add_money(self, operation: OperationCreate, user_id: int) -> dict:
        """Пополняет указанный кошелёк.

        После успешного пополнения инвалидирует кэш конкретного кошелька
        и кэш всех кошельков пользователя.

        Args:
            operation (OperationCreate): Данные операции пополнения.
            user_id (int): Идентификатор пользователя.

        Returns:
            dict: Результат операции (например, новый баланс).

        Raises:
            Исключения из репозитория, если операция не удалась.

        Notes:
            При успешном пополнении отправляет письмо на email пользователя.
        """

        res = await self.operation_repo.operations.add_money(operation, user_id)

        if res:
            # Инвалидация кэша конкретного wallet конкретного user
            key = f"fastapi-cache:wallets:wallet:{user_id}:{operation.wallet_name}"
            await FastAPICache.clear(key=key)

            # Инвалидация кэша всех wallet конкретного user
            await FastAPICache.clear(namespace=f"all-wallets:{user_id}")

            # Отправка email
            send_email_async.delay(
                res["wallet_user"].email,
                "Пополнение кошелька",
                f"Вы пополнили кошелек {operation.wallet_name} на сумму: {operation.amount}",
            )

            return res

    async def withdraw_money(self, operation: OperationCreate, user_id: int) -> dict:
        """Снимает деньги с указанного кошелька.

        После успешного снятия инвалидирует кэш конкретного кошелька
        и кэш всех кошельков пользователя.

        Args:
            operation (OperationCreate): Данные операции снятия.
            user_id (int): Идентификатор пользователя.

        Returns:
            dict: Результат операции (например, новый баланс).

        Raises:
            Исключения из репозитория, если операция не удалась.

        Notes:
            При успешном снятии отправляет письмо на email пользователя.
        """

        res = await self.operation_repo.operations.withdraw_money(operation, user_id)

        if res:
            # Инвалидация кэша конкретного wallet конкретного user
            key = f"fastapi-cache:wallets:wallet:{user_id}:{operation.wallet_name}"
            await FastAPICache.clear(key=key)

            # Инвалидация кэша всех wallet конкретного user
            await FastAPICache.clear(namespace=f"all-wallets:{user_id}")

            # Отправка email
            send_email_async.delay(
                res["wallet_user"].email,
                "Снятие денег с кошелька",
                body=f"Вы сняли {operation.amount} с кошелека {operation.wallet_name}",
            )

            return res

    async def transfer_money(self, transfer: TransferMoneyCreate, user_id: int) -> dict:
        """Переводит деньги между кошельками пользователя.

        После успешного перевода инвалидирует кэш обоих кошельков
        и кэш всех кошельков пользователя.

        Args:
            transfer (TransferMoneyCreate): Данные перевода.
            user_id (int): Идентификатор пользователя.

        Returns:
            dict: Результат операции (например, новые балансы).

        Raises:
            Исключения из репозитория, если операция не удалась.
        """
        res = await self.operation_repo.operations.transfer_money(transfer, user_id)

        if res:
            # Инвалидация кэша конкретного wallet конкретного user
            key_1 = f"fastapi-cache:wallets:wallet:{user_id}:{transfer.wallet_from}"
            await FastAPICache.clear(key=key_1)

            # Инвалидация кэша конкретного wallet конкретного user
            key_2 = f"fastapi-cache:wallets:wallet:{user_id}:{transfer.wallet_to}"
            await FastAPICache.clear(key=key_2)

            # Инвалидация кэша всех wallet конкретного user
            await FastAPICache.clear(namespace=f"all-wallets:{user_id}")

            return res
