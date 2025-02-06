import logging

from api.domain.MessageSent import MessageSent
from api.persistence.MessageSentPersistence import MessageSentPersistence


logger = logging.getLogger(__name__)

class MessageSentController(object):

    @classmethod
    def save(cls, message_sent: MessageSent) -> MessageSent:
        return MessageSentPersistence.save(message_sent=message_sent)
