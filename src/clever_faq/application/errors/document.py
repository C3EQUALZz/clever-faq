from clever_faq.application.errors.base import ApplicationError


class UnknownMimeTypeError(ApplicationError): ...


class DocumentNotFoundError(ApplicationError): ...
