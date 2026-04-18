from fastapi import HTTPException, status


class FinanceTrackerHTTPException(HTTPException):
    status_code = status.HTTP_418_IM_A_TEAPOT
    detail = "Error"

    def __init__(self):
        super().__init__(self.status_code, self.detail)


class WalletNotFoundHTTPException(FinanceTrackerHTTPException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, message: str):
        self.detail = message


class WalletAlreadyHTTPExistsException(FinanceTrackerHTTPException):
    status_code = status.HTTP_409_CONFLICT

    def __init__(self, wallet_name: str):
        self.detail = f"Wallet {wallet_name!r} Already Exists"


class InsufficientFundsHTTPException(FinanceTrackerHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, message: str):
        self.detail = message


class SameWalletHTTPException(FinanceTrackerHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Wallets Shoud Not Be The Same"


class UserAlreadyHTTPExistsException(FinanceTrackerHTTPException):
    status_code = status.HTTP_409_CONFLICT
    detail = "User With Such Email Already Exists"


class IncorrectCredentialsHTTPException(FinanceTrackerHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Incorrect email or password"
    headers = {"WWW-Authenticate": "Bearer"}


class CredentialsHTTPException(FinanceTrackerHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Could not validate refresh token"
    headers = {"WWW-Authenticate": "Bearer"}
