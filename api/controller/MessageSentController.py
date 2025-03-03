import logging

from api.domain.Lead import SystemLead
from api.domain.MessageSent import MessageSent

from api.persistence.MessageSentPersistence import MessageSentPersistence


logger = logging.getLogger(__name__)

class MessageSentController(object):

    @classmethod
    def save(cls, message_sent: MessageSent) -> MessageSent:
        return MessageSentPersistence.save(message_sent=message_sent)

    @classmethod
    def get_by_message_id(cls, lead: SystemLead, message_id: str) -> MessageSent:
        return MessageSentPersistence.get_by_message_id(lead=lead, message_id=message_id)

    @classmethod
    def exist(cls, lead: SystemLead, message_id: str) -> bool:
        return MessageSentPersistence.exist(lead=lead, message_id=message_id)
