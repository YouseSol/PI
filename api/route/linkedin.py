import logging

import fastapi
import pydantic

from api.APIConfig import APIConfig

from api.ai.Agency import OutboundSales
from api.exception.APIException import APIException

from api.thirdparty.UnipileService import UnipileService

from api.domain.Client import Client
from api.domain.Lead import Lead


logger = logging.getLogger(__name__)

router = fastapi.APIRouter(prefix="/linkedin", tags=[ "Linkedin" ])

class AnswerChatModel(pydantic.BaseModel):
    client: Client
    lead: Lead
    chat_id: str

@router.post("/answer-chat")
async def answer_chat(chat: AnswerChatModel):
    unipile_cfg: dict = APIConfig.get("Unipile")

    unipile = UnipileService(authorization_key=unipile_cfg["AuthorizationKey"],
                             subdomain=unipile_cfg["Subdomain"],
                             port=unipile_cfg["Port"])

    messages_in_chat = [
        dict(role="lead" if message["sender_id"] == chat.lead.linkedin_public_identifier else "agent",
             content=message["text"])
        for message in unipile.retrieve_chat_messages(chat_id=chat.chat_id, limit=10)["items"]
    ]

    if len(messages_in_chat) == 0:
        raise APIException("Asked to generate anwser to empty chat.", context=chat.model_dump())

    messages_compiled = [ messages_in_chat[0] ]
    remaining_messages = messages_in_chat[1::]

    for message in remaining_messages:
        if message["role"] == messages_compiled[-1]["role"]:
            messages_compiled[-1]["content"] = message["content"] + ". " + messages_compiled[-1]["content"]
        else:
            messages_compiled.append(message)

    chat_history = [
        { "role": "Cliente" if message["role"] == "lead" else "Prospector", "content": message["content"] }
        for message in messages_compiled
    ]

    outbound_sales_crew = OutboundSales(client=chat.client, lead=chat.lead, chat_history=chat_history).crew()

    crew_output = outbound_sales_crew.kickoff()

    # TODO: Implement AI.

    message = crew_output.raw

    logger.debug(f"Message Generated: {crew_output.raw}")

    unipile.send_message(chat_id=chat.chat_id, text=message)
