from app.schemas import WalletCreate, WalletPublic
from app.uow.uow import DBManager


class WalletService:
    """Сервис для бизнес-логики, связанной с кошельками.

    Предоставляет методы для управления кошельками пользователей,
    выступая как прослойка между API-обработчиками и репозиторием.
    Инкапсулирует бизнес-правила и координирует работу с другими
    сервисами при необходимости.

    Attributes:
        wallet_repo (DBManager): Менеджер базы данных для доступа к репозиторию кошельков.
    """

    def __init__(self, wallet_repo: DBManager):
        """Инициализирует сервис кошельков.

        Args:
            wallet_repo (DBManager): Экземпляр менеджера базы данных для доступа к данным.
        """
        self.wallet_repo = wallet_repo

    async def get_wallets(self, offset, limit, user_id: int) -> list[WalletPublic]:
        """Получает список кошельков пользователя с пагинацией.

        Args:
            offset: Смещение для пагинации.
            limit: Количество записей на странице.
            user_id (int): Идентификатор пользователя, чьи кошельки нужно получить.

        Returns:
            list[WalletPublic]: Список публичных представлений кошельков пользователя.
        """
        return await self.wallet_repo.wallets.get_all_wallets(offset, limit, user_id)

    async def get_wallet_by_name(self, wallet_name: str, user_id: int) -> WalletPublic:
        """Получает конкретный кошелек по имени для указанного пользователя.

        Args:
            wallet_name (str): Название кошелька для поиска.
            user_id (int): Идентификатор пользователя, которому принадлежит кошелек.

        Returns:
            WalletPublic: Публичное представление найденного кошелька.
        """
        return await self.wallet_repo.wallets.get_wallet_by_name(wallet_name, user_id)

    async def create_wallet(self, wallet: WalletCreate, user_id: int) -> WalletPublic:
        """Создает новый кошелек для пользователя.

        Args:
            wallet (WalletCreate): Данные для создания нового кошелька.
            user_id (int): Идентификатор пользователя, которому создается кошелек.

        Returns:
            WalletPublic: Публичное представление созданного кошелька.
        """
        return await self.wallet_repo.wallets.create_wallet(wallet, user_id)
