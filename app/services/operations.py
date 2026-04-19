from app.schemas import OperationCreate, TransferMoneyCreate, OperationsHistory
from app.uow.uow import DBManager


class OperationService:
    """Сервис для бизнес-логики, связанной с финансовыми операциями.

    Предоставляет методы для управления операциями (добавление, снятие,
    перевод средств) и получения истории операций. Выступает как прослойка
    между API-обработчиками и репозиторием, инкапсулируя бизнес-правила.

    Attributes:
        operation_repo (DBManager): Менеджер базы данных для доступа к репозиторию операций.
    """

    def __init__(self, operation_repo: DBManager):
        """Инициализирует сервис операций.

        Args:
            operation_repo (DBManager): Экземпляр менеджера базы данных для доступа к данным.
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
        """Получает историю операций пользователя с возможностью сортировки и фильтрации.

        Args:
            sort_param (str): Параметр для сортировки (например, 'created_at', 'amount').
            dir (str): Направление сортировки ('asc' или 'desc').
            offset (int): Смещение для пагинации.
            limit (int): Количество записей на странице.
            user_id (int): Идентификатор пользователя, чьи операции нужно получить.
            filter (str | None): Опциональный фильтр для поиска операций.

        Returns:
            list[OperationsHistory]: Список операций в формате истории.
        """
        return await self.operation_repo.operations.get_all_operations(
            sort_param,
            dir,
            offset,
            limit,
            user_id,
            filter,
        )

    async def add_money(self, operation: OperationCreate, user_id: int) -> dict:
        """Добавляет средства на кошелек пользователя.

        Args:
            operation (OperationCreate): Данные операции пополнения.
            user_id (int): Идентификатор пользователя, которому добавляются средства.

        Returns:
            dict: Результат операции с информацией о статусе.
        """
        return await self.operation_repo.operations.add_money(operation, user_id)

    async def withdraw_money(self, operation: OperationCreate, user_id: int) -> dict:
        """Снимает средства с кошелька пользователя.

        Args:
            operation (OperationCreate): Данные операции снятия.
            user_id (int): Идентификатор пользователя, с которого снимаются средства.

        Returns:
            dict: Результат операции с информацией о статусе.
        """
        return await self.operation_repo.operations.withdraw_money(operation, user_id)

    async def transfer_money(self, transfer: TransferMoneyCreate, user_id: int) -> dict:
        """Переводит средства между кошельками пользователя.

        Args:
            transfer (TransferMoneyCreate): Данные для перевода средств.
            user_id (int): Идентификатор пользователя, осуществляющего перевод.

        Returns:
            dict: Результат операции перевода с информацией о статусе.
        """
        return await self.operation_repo.operations.transfer_money(transfer, user_id)
