class FinanceTrackerException(Exception):
    detail = "Unknown Exception"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class WalletNotFoundException(FinanceTrackerException):
    detail = "Wallet not found"


class WalletAlreadyExists(FinanceTrackerException):
    detail = "Wallet Already Exists"
