import datetime as dt
import json
import logging

import fastapi

from api.APIConfig import APIConfig

from api.controller.CampaignController import CampaignController
from api.persistence.connector import get_redis_db

from api.controller.Controller import Controller
from api.controller.ClientController import ClientController
from api.controller.LeadController import LeadController

from api.exception.APIException import APIException
from api.exception.DuplicatingObjectException import DuplicatingObjectException
from api.exception.InexistentObjectException import InexistentObjectException
from api.exception.ThirdPartyError import ThirdPartyError

from api.thirdparty.UnipileService import UnipileService

from api.domain.Client import Client, SystemClient
from api.domain.Lead import Lead


logger = logging.getLogger(__name__)

router = fastapi.APIRouter(prefix="/webhook/linkedin", tags=[ "Webhook", "Linkedin" ])

# @router.post("/connection-event-from-alessia")
# async def on_linkedin_connection_event_from_alessia(event: dict):
#     event = extract_data_from_alessia_connection_event(event=event)
#
#     owner = ClientController.get(email=event["owner"])
#
#     if not owner.active:
#         logger.info(f"Recieving Alessia invite event from inactive Client: '{owner.email}'.")
#         return
#
#     unipile_cfg: dict = APIConfig.get("Unipile")
#
#     unipile = UnipileService(authorization_key=unipile_cfg["AuthorizationKey"],
#                              subdomain=unipile_cfg["Subdomain"],
#                              port=unipile_cfg["Port"])
#
#     lead_linkedin_profile: dict = extract_data_from_unipile_retrieve_profile(
#         linkedin_profile=unipile.retrieve_profile(account_retrieving=owner.linkedin_account_id, account_id=event["account_id"])
#     )
#
#     # INFO: We do not expect this to fail but in case it fails we enrich the context with event info.
#     try:
#         LeadController.create(Lead(
#             owner=owner.email,
#             campaing=event["campaign"],
#             linkedin_public_identifier=lead_linkedin_profile["public_identifier"],
#             first_name=lead_linkedin_profile["first_name"],
#             last_name=lead_linkedin_profile["last_name"],
#             headline=lead_linkedin_profile["headline"],
#             emails=lead_linkedin_profile["emails"],
#             phones=lead_linkedin_profile["phones"],
#         ))
#     except DuplicatingObjectException as e:
#         raise DuplicatingObjectException(message=e.message, context=dict(event=event, exc_context=e.context))
#
# def extract_data_from_alessia_connection_event(event: dict) -> dict:
#     extraction = dict()
#
#     event_owner: dict | None = event.get("LinkedInAccount")
#
#     if event_owner is None:
#         raise ThirdPartyError(message="Alessia event has no key: 'LinkedInAccount'.", context=event)
#
#     owner_email: str | None = event_owner.get("Email")
#
#     if owner_email is None:
#         raise ThirdPartyError(message="Alessia event has no key: 'Email'.", context=event)
#
#     extraction["owner"] = owner_email
#
#     lead_account_url = event.get("MemberUrl")
#
#     if lead_account_url is None:
#         raise ThirdPartyError(message="Alessia event has no key: 'MemberUrl'.", context=event)
#
#     try:
#         lead_account_id = lead_account_url.split("/")[4]
#     except IndexError:
#         raise ThirdPartyError(message="Could not extract 'lead_account_id' from event.", context=event)
#
#     extraction["account_id"] = lead_account_id
#
#     campaigns : list | None = event.get("MemberCampaigns")
#
#     if campaigns is None:
#         raise ThirdPartyError(message="Alessia event has no key: 'MemberCampaigns'.", context=event)
#
#     try:
#         campaign_name: str = campaigns[0]["CampaignName"]
#     except IndexError:
#         raise ThirdPartyError(message="List of campaign is empty.", context=event)
#     except KeyError:
#         raise ThirdPartyError(message="Object of campaing has no key: 'CampaignName'.", context=event)
#
#     extraction["campaign"] = campaign_name
#
#     return extraction
#
# def extract_data_from_unipile_retrieve_profile(linkedin_profile: dict) -> dict:
#     extraction = dict()
#
#     lead_public_identifier: str | None = linkedin_profile.get("public_identifier")
#
#     if lead_public_identifier is None:
#         raise ThirdPartyError(message="Linkedin profile retrieved from Unipile has no key: 'public_identifier'.", context=linkedin_profile)
#
#     extraction["linkedin_public_identifier"] = lead_public_identifier
#
#     lead_first_name: str | None = linkedin_profile.get("first_name")
#
#     if lead_first_name is None:
#         raise ThirdPartyError(message="Linkedin profile retrieved from Unipile has no key: 'first_name'.", context=linkedin_profile)
#
#     extraction["first_name"] = lead_first_name
#
#     lead_last_name: str | None = linkedin_profile.get("last_name")
#
#     if lead_last_name is None:
#         raise ThirdPartyError(message="Linkedin profile retrieved from Unipile has no key: 'last_name'.", context=linkedin_profile)
#
#     extraction["last_name"] = lead_last_name
#
#     lead_headline: str | None = linkedin_profile.get("headline")
#
#     if lead_headline is None:
#         raise ThirdPartyError(message="Linkedin profile retrieved from Unipile has no key: 'headline'.", context=linkedin_profile)
#
#     extraction["last_headline"] = lead_headline
#
#     lead_contact_info: dict = linkedin_profile.get("contact_info", dict())
#
#     extraction["emails"] = lead_contact_info.get("emails", list())
#     extraction["phones"] = lead_contact_info.get("phones", list())
#
#     return extraction

@router.post("/message-event-from-unipile")
def on_linkedin_message_event_from_unipile(event: dict):
    event = extract_data_from_unipile_message_event(event=event)

    logger.debug(event)

    try:
        client = ClientController.get_by_linkedin_account_id(linkedin_account_id=event["account_id"])
    except InexistentObjectException:
        logger.warn(f"Recieving Unipile message event from unkown Client: '{event['account_id']}'.")
        return

    if not client.active:
        logger.warn(f"Recieving Unipile message event from inactive Client: '{client.email}'.")
        return

    if event["event"] != "message_received":
        return

    if event["provider"] != "linkedin":
        logger.warn(f"Recieving Unipile events from different provider: '{(client.email, event['provider'])}'.")
        return

    if event['account_info_user_id'] == event['sender_linkedin_identifier']:
        logger.debug("My account received the notification of my message.")
        return

    lead_linkedin_public_identifier = event["sender_linkedin_identifier"]

    if not LeadController.is_a_valid_lead(owner=client.email, linkedin_public_identifier=lead_linkedin_public_identifier):
        return

    lead = LeadController.get_by_owner_and_linkedin_public_identifier(
        owner=client.email,
        linkedin_public_identifier=lead_linkedin_public_identifier
    )

    lead.chat_id = event["chat_id"]

    LeadController.save(lead=lead)

    campaign = CampaignController.get_by_id(owner=client.email, id=lead.campaign)

    if not campaign.active:
        return

    if lead.active and campaign.active:
        mark_chat_to_be_answered(client=client, lead=lead, chat_id=event["chat_id"], datetime=event["datetime"])

    Controller.save()

def extract_data_from_unipile_message_event(event: dict) -> dict:
    extraction = dict()

    event_type: str | None = event.get("event")

    if event_type is None:
        raise ThirdPartyError(message="Unipile message event has no key: 'event'.", context=event)

    extraction["event"] = event_type

    message: str | None = event.get("message")

    if message is None:
        raise ThirdPartyError(message="Unipile message event has no key: 'message'.", context=event)

    extraction["message"] = message

    provider: str | None = event.get("account_type")

    if provider is None:
        raise ThirdPartyError(message="Unipile message event has no key: 'account_type'.", context=event)

    extraction["provider"] = provider.lower()

    account_id: str | None = event.get("account_id")

    if account_id is None:
        raise ThirdPartyError(message="Unipile message event has no key: 'account_id'.", context=event)

    extraction["account_id"] = account_id

    chat_id: str | None = event.get("chat_id")

    if chat_id is None:
        raise ThirdPartyError(message="Unipile message event has no key: 'chat_id'.", context=event)

    extraction["chat_id"] = chat_id

    # ----- x -----

    account_info: dict | None = event.get("account_info")

    if account_info is None:
        raise ThirdPartyError(message="Unipile message event has no key: 'account_info'.", context=event)

    account_info_user_id = account_info.get("user_id")

    if account_info_user_id is None:
        raise ThirdPartyError(message="Unipile acount_info has no key: 'user_id'.", context=event)

    extraction["account_info_user_id"] = account_info_user_id

    # ----- x -----

    sender: dict | None = event.get("sender")

    if sender is None:
        raise ThirdPartyError(message="Unipile message event has no key: 'sender'.", context=event)

    sender_linkedin_public_identifier = sender.get("attendee_provider_id")

    if sender_linkedin_public_identifier is None:
        raise ThirdPartyError(message="Unipile message event has no key: 'attendee_provider_id'.", context=event)

    extraction["sender_linkedin_identifier"] = sender_linkedin_public_identifier

    # ----- x -----

    timestamp = event.get("timestamp")

    if timestamp is None:
        raise ThirdPartyError(message="Unipile message event has no key: 'timestamp'.", context=event)

    extraction["datetime"] = dt.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")

    return extraction

def mark_chat_to_be_answered(client: SystemClient, lead: Lead, chat_id: str, datetime: dt.datetime):
    redis_db = get_redis_db()

    key = f"TASK_TRIGGER_CHAT_ANSWER-{client.email}-{lead.linkedin_public_identifier}-{lead.id}"

    task_str: str | None = redis_db.get(key)

    if task_str is not None:
        task = json.loads(task_str)

        if datetime.timestamp() < task["timestamp"]:
            return

    client_d = client.model_dump()
    client_d.pop("created_at") # INFO: DateTime is not JSONSerializable. Do no work with json.dumps

    value = dict(client=client_d, lead=lead.model_dump(), timestamp=datetime.timestamp())

    if not redis_db.set(key, json.dumps(value)):
        raise APIException(f"Failed to add task into redis. Key: {key}", context=value)
