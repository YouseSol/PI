import datetime as dt, io, json, logging, typing as t, time, zipfile

import fastapi, pydantic, openpyxl, requests

from appconfig import AppConfig

from api.thirdparty.connector import get_unipile

from api.persistence.connector import get_redis_db

from api.domain.Client import Client
from api.domain.Campaign import Campaign
from api.domain.Lead import Lead, SystemLead
from api.domain.FailedLead import FailedLead

from api.route.responses import CountResponse, CampaignsResponse, LeadsResponse

from api.controller.Controller import Controller
from api.controller.ClientController import ClientController
from api.controller.CampaignController import CampaignController
from api.controller.LeadController import LeadController
from api.controller.FailedLeadController import FailedLeadController
from api.controller.ContactController import ContactController

from api.exception.ThirdPartyError import ThirdPartyError


logger = logging.getLogger(__name__)

router = fastapi.APIRouter(prefix="/campaign", tags=[ "Campaigns" ])

@router.post("/from-file/{campaign_name}")
async def post(campaign_name: str,
               file: fastapi.UploadFile,
               pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()],
               background_tasks: fastapi.BackgroundTasks):
    client = ClientController.get_by_api_token(api_token=pi_api_token)

    if CampaignController.exists(client=client, name=campaign_name):
        raise fastapi.exceptions.HTTPException(status_code=409, detail="Already exists campaign with that name.")

    _bytes = file.file.read()

    validate_campaing_file(_bytes)

    background_tasks.add_task(insert_campaign, file=_bytes, campaign_name=campaign_name, api_token=pi_api_token)

def insert_campaign(campaign_name: str, file: bytes, api_token: pydantic.UUID4):
    redis_db = get_redis_db()

    client = ClientController.get_by_api_token(api_token=api_token)

    campaign = CampaignController.save(campaign=Campaign(owner=client.email, name=campaign_name, created_at=dt.datetime.now(), active=True))

    unipile_cfg: dict = AppConfig["Unipile"]

    key = f"LEAD-LOADING-{client.email}-{campaign.name}"

    execution = dict(status="LOADING", progress=0.0)

    redis_db.set(key, json.dumps(execution))

    sheet = openpyxl.open(io.BytesIO(file))["Sheet"]

    rows = list(filter(any, list(sheet.iter_rows(min_row=2, values_only=True))))

    failed_leads: list[FailedLead] = list()

    unipile = get_unipile()

    send_failed_to_load_email = lambda : \
        ContactController.send_email_to_client(
            subject="Prospector Inteligente: Falha ao carregar a campanha.",
            body=f"Algo falhou ao carregar a campanha: '{campaign_name}' do perfil '{client.first_name} {client.last_name}'.\n"
                  "Por favor, tente novamente mais tarde ou entre em contato com o suporte.",
            client=client
        )

    i = 0

    while i < len(rows):
        execution["progress"] = (i + 1) / len(rows)
        execution["status"] = "DONE" if i + 1 == len(rows) else "LOADING"

        redis_db.set(key, json.dumps(execution))

        row = rows[i]

        lead_linkedin_url = str(row[8])

        lead_account_id = lead_linkedin_url.split("/")[-1]

        try:
            # INFO: This call can fail and we dont know why. Occured for a specific profile. Maybe privace involved.
            lead_linkedin_profile: dict = extract_data_from_unipile_retrieve_profile(
                linkedin_profile=unipile.retrieve_profile(account_retrieving=client.linkedin_account_id, account_id=lead_account_id)
            )
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 422:
                failed_lead = FailedLead(campaign=campaign.id, first_name=str(row[1]), last_name=str(row[2]), profile_url=str(row[8]))
                FailedLeadController.save(failed_lead=failed_lead)
                failed_leads.append(failed_lead)
                i = i + 1
                continue

            raise
        except:
            send_failed_to_load_email()
            raise

        lead = SystemLead(campaign=campaign.id,
                          linkedin_public_identifier=lead_linkedin_profile["linkedin_identifier"],
                          first_name=lead_linkedin_profile["first_name"],
                          last_name=lead_linkedin_profile["last_name"],
                          emails=lead_linkedin_profile["emails"],
                          phones=lead_linkedin_profile["phones"],
                          active=True,
                          deleted=False,
                          chat_id=None)

        LeadController.save(lead)

        i = i + 1

    Controller.save()

    subject = f"Prospector Inteligente - Campanha carregada com sucesso: '{campaign_name}'."
    body = f"Todos os contatos da campanha: '{campaign_name}' do perfil '{client.first_name} {client.last_name}' foram carregados com sucesso.\n"

    if failed_leads:
        subject = f"Prospector Inteligente - Falha ao carregar alguns contatos da campanha: '{campaign_name}'."
        body = "Mensagem automática:\n" \
              f"Não foi possível carregar todos os contatos da campanha: '{campaign_name}' do perfil '{client.first_name} {client.last_name}'.\n" \
              + f"\nNo total foram carregados {100.0 * (1.0 - (len(failed_leads) / len(rows)))}% de todos os contatos.\n" \
              + "Os seguintes falharam:\n" \
              + '\n'.join([ f"{i + 1}) Nome: '{l.first_name} {l.last_name}' / Perfil: '{l.profile_url}'" for i, l in enumerate(failed_leads) ])

    ContactController.send_email_to_client(subject=subject,body=body, client=client)

def validate_campaing_file(file: bytes):
    try:
        sheet = openpyxl.open(io.BytesIO(file))["Sheet"]
    except zipfile.BadZipFile:
        raise fastapi.HTTPException(
            status_code=422,
            detail=f"Uploaded file do not match expected format: Expected an spreadsheet."
        )
    except KeyError:
        raise fastapi.HTTPException(
            status_code=422,
            detail=f"Uploaded file do not match expected format: Missing sheet named 'Sheet'."
        )

    first_row = list(next(sheet.iter_rows(min_row=1, max_row=1, values_only=True)))

    headers_tested_against = [
        'LinkedInMemberId',
        'First name', 'Last name',
        'Title', 'Company', 'Occupation',
        'Email', 'Phone',
        'LinkedIn URL',
        'Status',
        'ConnectedAtDate',
        'ConnectedAtTime'
    ]

    if len(first_row) != len(headers_tested_against):
        raise fastapi.HTTPException(
            status_code=422,
            detail=f"Uploaded file do not match expected format: '{headers_tested_against}'"
        )

    for i in range(len(headers_tested_against)):
        if (headers_tested_against[i] != first_row[i]):
            raise fastapi.HTTPException(
                status_code=422,
                detail=f"Uploaded file do not match expected format: '{headers_tested_against}'"
            )

def extract_data_from_unipile_retrieve_profile(linkedin_profile: dict) -> dict:
    extraction = dict()

    lead_provider_id: str | None = linkedin_profile.get("provider_id")

    if lead_provider_id is None:
        raise ThirdPartyError(message="Linkedin profile retrieved from Unipile has no key: 'provider_id'.", context=linkedin_profile)

    extraction["linkedin_identifier"] = lead_provider_id

    lead_first_name: str | None = linkedin_profile.get("first_name")

    if lead_first_name is None:
        raise ThirdPartyError(message="Linkedin profile retrieved from Unipile has no key: 'first_name'.", context=linkedin_profile)

    extraction["first_name"] = lead_first_name

    lead_last_name: str | None = linkedin_profile.get("last_name")

    if lead_last_name is None:
        raise ThirdPartyError(message="Linkedin profile retrieved from Unipile has no key: 'last_name'.", context=linkedin_profile)

    extraction["last_name"] = lead_last_name

    lead_contact_info: dict = linkedin_profile.get("contact_info", dict())

    extraction["emails"] = lead_contact_info.get("emails", list())
    extraction["phones"] = lead_contact_info.get("phones", list())

    return extraction

class CampaignNaming(pydantic.BaseModel):
    name: str

@router.put("/{campaign_name}/name")
async def put(campaign_name: str,
              naming: CampaignNaming,
              pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]) -> Campaign:
    client = ClientController.get_by_api_token(api_token=pi_api_token)

    if not CampaignController.exists(client=client, name=campaign_name):
        raise fastapi.exceptions.HTTPException(status_code=404, detail=f"Could not find campaign with name: '{campaign_name}'.")

    campaign = CampaignController.get_by_name(client=client, name=campaign_name)

    campaign = CampaignController.update_name(campaign=campaign, new_name=naming.name)

    Controller.save()

    return Campaign(**campaign.dict(include=Campaign.__fields__.keys()))


@router.delete("/{name}")
async def delete(name: str, pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]):
    raise fastapi.exceptions.HTTPException(status_code=501, detail="Not implemented yet.")

    client = ClientController.get_by_api_token(api_token=pi_api_token)

    campaign = CampaignController.get_by_name(name=name, owner=client.email)

    CampaignController.delete(campaign=campaign)

    Controller.save()

@router.get("/all/")
async def get_all(pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]) -> CampaignsResponse:
    client = ClientController.get_by_api_token(api_token=pi_api_token)

    campaigns = CampaignController.get_all(client=client)

    return CampaignsResponse(campaigns=[ Campaign(**system_campaign.dict(include=Campaign.__fields__.keys())) for system_campaign in campaigns ])

@router.get("/{name}/leads/count")
async def count_leads(name: str, pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]) -> CountResponse:
    client = ClientController.get_by_api_token(api_token=pi_api_token)

    campaign = CampaignController.get_by_name(client=client, name=name)

    return CountResponse(count=LeadController.count_leads_in_campaign(campaign=campaign))

@router.get("/{name}/leads")
async def get(name: str,
              page_size: int, page: int,
              pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()],
              query: str | None = None,
              has_conversation: bool | None = None,
              is_active: bool | None = None) -> LeadsResponse:
    client = ClientController.get_by_api_token(api_token=pi_api_token)

    campaign = CampaignController.get_by_name(client=client, name=name)

    leads = LeadController.paginate_leads_in_campaign(
        campaign=campaign,
        page_size=page_size, page=page,
        query=query,
        has_conversation=has_conversation,
        is_active=is_active
    )

    return LeadsResponse(leads=[ Lead(**system_lead.dict(include=Lead.__fields__.keys())) for system_lead in leads ])

@router.get("/{name}/answered-chats/count")
async def get_answered_chats(name: str, pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]) -> CountResponse:
    client = ClientController.get_by_api_token(api_token=pi_api_token)

    campaign = CampaignController.get_by_name(client=client, name=name)

    return CountResponse(count=CampaignController.count_answered_chats(campaign=campaign))

class MessagesPerDayItem(pydantic.BaseModel):
    date: dt.date
    count: int

class MessagesPerDayResponse(pydantic.BaseModel):
    messagesPerDay : list[MessagesPerDayItem]

@router.get("/{name}/messages-per-day")
async def get_messages_per_day(name: str,
                               since: dt.date, before: dt.date,
                               pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]) \
                               -> MessagesPerDayResponse:
    client = ClientController.get_by_api_token(api_token=pi_api_token)

    campaign = CampaignController.get_by_name(client=client, name=name)

    history_response = [
        MessagesPerDayItem(date=day["date"], count=day["messages_sent"])
        for day in CampaignController.count_messages_per_day(campaign=campaign, since=since, before=before)
    ]

    return MessagesPerDayResponse(messagesPerDay=history_response)
