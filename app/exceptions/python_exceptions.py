from decimal import Decimal


class FinanceTrackerException(Exception):
    detail = "Unknown Exception"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class WalletNotFoundException(FinanceTrackerException):
    detail = "Wallet Not Found"

    def __init__(self, name: str):
        self.detail = f"Wallet {name!r} Not Found"


class WalletAlreadyExistsException(FinanceTrackerException):
    detail = "Wallet Already Exists"


class InsufficientFundsException(FinanceTrackerException):
    def __init__(self, name: str, balance: Decimal):
        self.detail = f"Insufficient Funds. Wallet {name!r} balance: {balance}"


class SameWalletException(FinanceTrackerException):
    detail = "Wallets Shoud Not Be The Same"
