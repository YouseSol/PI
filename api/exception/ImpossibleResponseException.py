from api.exception.APIException import APIException


class ImpossibleResponseException(APIException):

    def __init__(self, message: str, context: dict | None = None):
        super().__init__(message=message, context=context)
