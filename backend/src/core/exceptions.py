class AppError(Exception):
    """کلاس پایه‌ی همه‌ی خطاهای دامنه‌ی برنامه."""
    status_code: int = 400

    def __init__(self, message: str = ""):
        self.message = message or self.__class__.__name__
        super().__init__(self.message)


class RegistrationNotFoundError(AppError):
    status_code = 404


class DuplicateRegistrationError(AppError):
    status_code = 409


class CapacityFullError(AppError):
    status_code = 409


class InvalidPaymentAmountError(AppError):
    status_code = 400


class InsufficientBalanceError(AppError):
    status_code = 400


class TripNotFoundError(AppError):
    status_code = 404


class UserNotFoundError(AppError):
    status_code = 404


class InvalidCredentialsError(AppError):
    status_code = 401
