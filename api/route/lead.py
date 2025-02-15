import datetime as dt, logging, typing as t

import fastapi, pydantic

from appconfig import AppConfig

from api.domain.Lead import Lead

from api.controller.Controller import Controller
from api.controller.ClientController import ClientController
from api.controller.LeadController import LeadController
from api.thirdparty.connector import get_unipile


logger = logging.getLogger(__name__)

router = fastapi.APIRouter(prefix="/lead", tags=[ "Leads" ])

@router.get("/")
async def get(page_size: int, page: int, pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]) -> dict[str, list[Lead]]:
    client = ClientController.get_by_api_token(api_token=pi_api_token)
    return dict(leads=LeadController.get(owner=client.email, page_size=page_size, page=page))

@router.post("/")
async def post(lead: Lead, pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]) -> Lead:
    client = ClientController.get_by_api_token(api_token=pi_api_token)

    l =  LeadController.save(lead=lead)

    Controller.save()

    return l

@router.delete("/")
async def delete(lead: Lead, pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]) -> Lead:
    client = ClientController.get_by_api_token(api_token=pi_api_token)

    l = LeadController.delete(lead=lead)

    Controller.save()

    return l

@router.get("/{lead_id}/chat")
def get_chat(lead_id: int, pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]) -> dict:
    client = ClientController.get_by_api_token(api_token=pi_api_token)

    lead = LeadController.get_by_id(owner=client.email, id=lead_id)

    if lead.chat_id is None:
        return dict(messages=list())

    unipile = get_unipile()

    chat_history = unipile.retrieve_chat_messages(chat_id=lead.chat_id, limit=250)["items"]

    messages_in_chat = [
        dict(role="lead" if message["sender_id"] == lead.linkedin_public_identifier else "agent",
            content=message["text"],
            timestamp=int(dt.datetime.fromisoformat(message["timestamp"]).timestamp()))
        for message in chat_history
    ]

    messages_in_chat.sort(key=lambda m: m["timestamp"])

    return dict(messages=messages_in_chat)
