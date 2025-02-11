import logging

from api.controller.ContactController import ContactController

logger = logging.getLogger(__name__)


class EmailHandler(logging.Handler):

    def emit(self, record: logging.LogRecord) -> None:
        if record.levelno not in (logging.ERROR, logging.CRITICAL, logging.FATAL):
            return

        subject: str | None = getattr(record, "subject", None)
        body: str | None = getattr(record, "body", None)

        if (subject is None) or (body is None):
            subject = "PI API - Improper usage of logger."
            body = f"Improper usage of logger in file '{record.filename}' at line '{record.lineno}' when executing '{record.funcName}'."

        ContactController.send_email_to_support(subject=subject, body=body)
