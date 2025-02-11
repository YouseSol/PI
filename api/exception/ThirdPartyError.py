from api.exception.APIException import APIException


class ThirdPartyError(APIException):
    """ Generic error for third party errors. """

    def __init__(self, message: str, context: dict | None = None):
        super().__init__(message=message, context=context)
