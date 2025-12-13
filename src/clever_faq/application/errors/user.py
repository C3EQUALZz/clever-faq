from clever_faq.application.errors.base import ApplicationError


class UserAlreadyExistsError(ApplicationError): ...


class UserNotFoundByEmailError(ApplicationError): ...


class UserNotFoundByIDError(ApplicationError): ...
