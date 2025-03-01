import datetime as dt, logging, typing as t

import fastapi, pydantic

from api.controller.MessageSentController import MessageSentController
from api.exception.InexistentObjectException import InexistentObjectException
from appconfig import AppConfig

from api.thirdparty.connector import get_unipile

from api.domain.Lead import Lead, SystemLead

from api.controller.Controller import Controller
from api.controller.ClientController import ClientController
from api.controller.LeadController import LeadController


logger = logging.getLogger(__name__)

router = fastapi.APIRouter(prefix="/lead", tags=[ "Leads" ])

@router.put("/")
async def put(lead: Lead, pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]) -> Lead:
    client = ClientController.get_by_api_token(api_token=pi_api_token)

    system_lead = LeadController.get_by_id(client=client, id=lead.id)

    if id == 0:
        raise fastapi.HTTPException(status_code=404, detail=f"Could not find Lead with id: '{lead.id}'.")

    system_lead.first_name = lead.first_name
    system_lead.last_name = lead.last_name
    system_lead.emails = lead.emails
    system_lead.phones = lead.phones
    system_lead.active = lead.active
    system_lead.feedback = lead.feedback

    l =  LeadController.save(lead=system_lead)

    Controller.save()

    return l

@router.delete("/{id}")
async def delete(id: int, pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]):
    client = ClientController.get_by_api_token(api_token=pi_api_token)

    system_lead = LeadController.get_by_id(client=client, id=id)

    LeadController.delete(lead=system_lead)

    Controller.save()

class Message(pydantic.BaseModel):
    id: str
    role: t.Literal["lead"] | t.Literal["client"]
    content: str
    timestamp: int

class MessagesResponse(pydantic.BaseModel):
    messages: list[Message]

@router.get("/{id}/chat")
def get_chat(id: int, pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]) -> MessagesResponse:
    client = ClientController.get_by_api_token(api_token=pi_api_token)

    lead = LeadController.get_by_id(client=client, id=id)

    if lead.chat_id is None:
        return MessagesResponse(messages=list())

    unipile = get_unipile()

    chat_history = unipile.retrieve_chat_messages(chat_id=lead.chat_id, limit=250)["items"]

    messages_in_chat = [
        Message(id=message["id"],
                role="lead" if message["sender_id"] == lead.linkedin_public_identifier else "client",
                content=message["text"],
                timestamp=int(dt.datetime.fromisoformat(message["timestamp"]).timestamp()))
        for message in chat_history
    ]

    messages_in_chat.sort(key=lambda m: m.timestamp)

    return MessagesResponse(messages=messages_in_chat)

class MessageToLead(pydantic.BaseModel):
    content: str

@router.post("/{id}/chat")
def post_chat_message(id: int, message: MessageToLead, pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]):
    client = ClientController.get_by_api_token(api_token=pi_api_token)

    try:
        lead = LeadController.get_by_id(client=client, id=id)
    except InexistentObjectException:
        raise fastapi.HTTPException(status_code=404, detail=f"Lead not found with id: '{id}'")

    if lead.chat_id is None:
        raise fastapi.HTTPException(status_code=409, detail=f"Lead with id '{id}' has not interacted back.")

    unipile = get_unipile()

    message_sent_data = unipile.send_message(chat_id=lead.chat_id, text=message.content)

    raise fastapi.HTTPException(status_code=501)

class FeedbackToMessage(pydantic.BaseModel):
    content: str

@router.post("/{lead_id}/chat/{message_id}")
def post_message_feedback(lead_id: int, message_id: str,
                          feedback: FeedbackToMessage,
                          pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]):
    client = ClientController.get_by_api_token(api_token=pi_api_token)

    try:
        lead = LeadController.get_by_id(client=client, id=lead_id)
    except InexistentObjectException:
        raise fastapi.HTTPException(status_code=404, detail=f"Lead not found with id: '{lead_id}'")

    message_sent = MessageSentController.get_by_message_id(lead=lead, message_id=message_id)

    message_sent.feedback = feedback.content

    MessageSentController.save(message_sent=message_sent)

    Controller.save()

class FeedbackToChat(pydantic.BaseModel):
    is_positive: bool

@router.post("/{id}/chat/feedback/")
def post_chat_feedback(id: int, feedback: FeedbackToChat, pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]):
    client = ClientController.get_by_api_token(api_token=pi_api_token)

    try:
        lead = LeadController.get_by_id(client=client, id=id)
    except InexistentObjectException:
        raise fastapi.HTTPException(status_code=404, detail=f"Lead not found with id: '{id}'")

    lead.feedback = feedback.is_positive

    LeadController.save(lead=lead)

    Controller.save()
