class APIException(Exception):
    """ Generic error for api exceptions. """

    def __init__(self, message: str, context: dict | None = None):
        super().__init__()

        self.message = message
        self.context = context

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.message} / Context: {self.context}"

    def __repr__(self) -> str:
        return str(self)
