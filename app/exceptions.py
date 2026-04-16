from fastapi import HTTPException, status


class FinanceTrackerException(Exception):
    detail = "Unknown Exception"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class WalletNotFoundException(FinanceTrackerException):
    detail = "Wallet Not Found"


class WalletAlreadyExists(FinanceTrackerException):
    detail = "Wallet Already Exists"


class FinanceTrackerHTTPException(HTTPException):
    status_code = status.HTTP_418_IM_A_TEAPOT
    detail = "Error"

    def __init__(self):
        super().__init__(self.status_code, self.detail)


class WalletNotFoundHTTPException(FinanceTrackerHTTPException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, wallet_name: str):
        self.detail = f"Wallet {wallet_name!r} Not Found"


class WalletAlreadyHTTPExists(FinanceTrackerHTTPException):
    status_code = status.HTTP_409_CONFLICT

    def __init__(self, wallet_name: str):
        self.detail = f"Wallet {wallet_name!r} Already Exists"
