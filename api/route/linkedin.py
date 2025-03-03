import datetime as dt, json, logging

import fastapi, pydantic

from api.controller.ContactController import ContactController
from api.controller.LeadController import LeadController
from appconfig import AppConfig

from api.thirdparty.connector import get_unipile

from api.domain.Client import SystemClient
from api.domain.Lead import SystemLead
from api.domain.MessageSent import MessageSent

from api.ai.IntentAnalyzerAgency import IntentAnalyzerAgency
from api.ai.OutboundSalesAgency import OutboundSalesAgency
from api.ai.ValidationAgency import ValidationAgency

from api.controller.Controller import Controller
from api.controller.MessageSentController import MessageSentController

from api.exception.APIException import APIException


logger = logging.getLogger(__name__)

router = fastapi.APIRouter(prefix="/linkedin", tags=[ "Linkedin" ])

class AnswerChatModel(pydantic.BaseModel):
    client: SystemClient
    lead: SystemLead

@router.post("/answer-chat")
async def answer_chat(chat: AnswerChatModel):
    if chat.lead.chat_id is None:
        raise APIException("Received an chat to answer without the 'chat_id' attribute.")

    unipile = get_unipile()

    messages_in_chat = [
        dict(role="lead" if message["sender_id"] == chat.lead.linkedin_public_identifier else "agent",
             content=message["text"],
             date=dt.datetime.fromisoformat(message["timestamp"]))
        for message in unipile.retrieve_chat_messages(chat_id=chat.lead.chat_id, limit=10)["items"]
        if message["text"] is not None
    ]

    messages_in_chat.sort(key=lambda m: m["date"])

    if len(messages_in_chat) == 0:
        raise APIException("Asked to generate anwser to empty chat.", context=chat.model_dump())

    messages_compiled = [ messages_in_chat[0] ]
    remaining_messages = messages_in_chat[1::]

    for message in remaining_messages:
        if message["role"] == messages_compiled[-1]["role"]:
            messages_compiled[-1]["content"] = messages_compiled[-1]["content"] + ". " + message['content']
        else:
            messages_compiled.append(message)

    chat_history = [
        { "role": "Cliente" if message["role"] == "lead" else "Prospector", "content": message["content"] }
        for message in messages_compiled
    ]

    if chat_history[-1]["role"] == "Prospector":
        logger.debug(f"{chat.client.email, chat.lead.first_name}\n" \
                      "The last message was sent by the agent or someone with access to the account answered before the agent.")
        return

    # DISCUSSION: All the AI part should be a single call, that returns an object that say:
    #  1. If it should answer or not to the message.
    #  2. If it shoul deactivate lead and send email.
    #  etc.

    intent_analyzer_crew = IntentAnalyzerAgency(conversation_history=chat_history).crew()

    intent_analyzer_output = intent_analyzer_crew.kickoff().raw

    if bool(intent_analyzer_output):
        ContactController.send_email_to_client(
            client=chat.client,
            subject="[PI] Um lead gostaria de marcar uma reunião para conversar.",
            body=f"Olá!\n"
                 f"Você esta recebendo este email porque o lead '{chat.lead.first_name} {chat.lead.last_name}' "
                 f"do perfil '{chat.client.first_name} {chat.client.last_name}' "
                  "gostaria de marcar uma reunião."
        )

        chat.lead.active = False

        LeadController.save(chat.lead)

        Controller.save()

        return

    # BUG: When will the AI stop answering if the lead does not want to talk anymore?

    outbound_sales_crew = OutboundSalesAgency(client=chat.client, lead=chat.lead, chat_history=chat_history).crew()
    outbound_sales_output = outbound_sales_crew.kickoff().raw

    logger.debug(f"Outbound Sales Message Generated:\n{outbound_sales_output}")

    validation_crew = ValidationAgency(lead=chat.lead, message=outbound_sales_output).crew()
    validation_output = validation_crew.kickoff().raw

    logger.debug(f"Validation Message Generated:\n{validation_output}")

    message = validation_output

    message_sent_data = unipile.send_message(chat_id=chat.lead.chat_id, text=message)

    MessageSentController.save(message_sent=MessageSent(id=message_sent_data["message_id"], lead=chat.lead.id, sent_at=dt.datetime.now()))

    Controller.save()
