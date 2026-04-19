from app.repository.wallet import WalletRepository
from app.repository.operation import OperationRepository
from app.repository.user import UserRepository


class DBManager:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):

        self.session = self.session_factory()

        self.wallets = WalletRepository(self.session)
        self.users = UserRepository(self.session)
        self.operations = OperationRepository(self.session)

        return self

    async def __aexit__(self, exc_type, *args):
        try:
            if exc_type:
                await self.rollback()
            else:
                await self.commit()
        finally:
            await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    def add(self, obj):
        self.session.add(obj)

    async def flush(self):
        await self.session.flush()
