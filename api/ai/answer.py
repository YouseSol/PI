from api.domain.ChatAction import ChatAction

from api.domain.Client import SystemClient
from api.domain.Lead import SystemLead


def answer(client: SystemClient, lead: SystemLead, chat_history: list[dict]) -> ChatAction:
    raise NotImplementedError()

    return ChatAction(should_answer=False, message="TODO")
