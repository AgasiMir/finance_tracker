from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Wallet
from app.schemas import WalletPublic, WalletCreate
from app.exceptions.python_exceptions import (
    WalletNotFoundException,
    WalletAlreadyExistsException,
)


class WalletRepository:
    """Репозиторий для работы с кошельками пользователей.
    Предоставляет методы для CRUD-операций с кошельками в базе данных.
    """

    def __init__(self, db: AsyncSession):
        """Инициализирует репозиторий с сессией базы данных.

        Args:
            db (AsyncSession): Асинхронная сессия SQLAlchemy.
        """
        self.db = db

    @staticmethod
    def _from_db(model: Wallet) -> WalletPublic:
        """Преобразует модель Wallet в схему WalletPublic.

        Args:
            model (Wallet): Модель кошелька из базы данных.

        Returns:
            WalletPublic: Валидированная схема для публичного представления.
        """
        return WalletPublic.model_validate(model)

    async def is_wallet_exist(self, wallet_name: str, user_id: int) -> Wallet:
        """Проверяет, существует ли кошелёк с указанным именем у пользователя.

        Args:
            wallet_name (str): Название кошелька.
            user_id (int): Идентификатор пользователя.

        Returns:
            Wallet | None: Модель кошелька, если найден, иначе None.
        """
        return await self.db.scalar(
            select(Wallet).where(
                Wallet.name == wallet_name,
                Wallet.user_id == user_id,
            )
        )

    async def get_wallet_by_name(self, wallet_name: str, user_id: int) -> WalletPublic:
        """Возвращает кошелёк по имени для указанного пользователя.

        Args:
            wallet_name (str): Название кошелька.
            user_id (int): Идентификатор пользователя.

        Returns:
            WalletPublic: Публичное представление кошелька.

        Raises:
            WalletNotFoundException: Если кошелёк не найден.
        """
        wallet = await self.db.scalar(
            select(Wallet).where(
                Wallet.name == wallet_name,
                Wallet.user_id == user_id,
            )
        )
        if not wallet:
            raise WalletNotFoundException(wallet_name)

        return self._from_db(wallet)

    async def get_all_wallets(self, offset, limit, user_id: int) -> list[WalletPublic]:
        """Возвращает список кошельков пользователя с пагинацией.

        Args:
            offset: Смещение для пагинации.
            limit: Количество записей на странице.
            user_id (int): Идентификатор пользователя.

        Returns:
            list[WalletPublic]: Список публичных представлений кошельков.
        """
        wallets = await self.db.scalars(
            select(Wallet)
            .where(Wallet.user_id == user_id)
            .order_by(Wallet.id)
            .offset(offset)
            .limit(limit)
        )
        return [self._from_db(obj) for obj in wallets.all()]

    async def create_wallet(self, wallet: WalletCreate, user_id: int) -> WalletPublic:
        """Создаёт новый кошелёк для пользователя.

        Args:
            wallet (WalletCreate): Данные для создания кошелька.
            user_id (int): Идентификатор пользователя.

        Returns:
            WalletPublic: Созданный кошелёк в публичном представлении.

        Raises:
            WalletAlreadyExistsException: Если кошелёк с таким именем уже существует.
        """
        if await self.is_wallet_exist(wallet.name, user_id):
            raise WalletAlreadyExistsException

        db_wallet = Wallet(**wallet.model_dump(), user_id=user_id)
        self.db.add(db_wallet)
        await self.db.flush()

        return self._from_db(db_wallet)
