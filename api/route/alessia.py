import datetime as dt, io, json, logging, typing as t, time, zipfile

import fastapi
import pydantic

import openpyxl
import requests

from api.APIConfig import APIConfig

from api.controller.CampaignController import CampaignController
from api.controller.ContactController import ContactController
from api.controller.FailedLeadController import FailedLeadController
from api.domain.Campaign import Campaign
from api.domain.FailedLead import FailedLead
from api.persistence.connector import get_redis_db

from api.controller.Controller import Controller

from api.controller.ClientController import ClientController
from api.controller.LeadController import LeadController

from api.exception.ThirdPartyError import ThirdPartyError

from api.thirdparty.UnipileService import UnipileService

from api.domain.Client import Client
from api.domain.Lead import Lead


logger = logging.getLogger(__name__)

router = fastapi.APIRouter(prefix="/alessia", tags=[ "Alessia" ])

@router.post("/activate-leads/{campaign_name}")
async def activate_leads(campaign_name: str,
                         file: fastapi.UploadFile,
                         pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()],
                         background_tasks: fastapi.BackgroundTasks):
    client = ClientController.get_by_api_token(api_token=pi_api_token)

    if CampaignController.exists(name=campaign_name, owner=client.email):
        raise fastapi.exceptions.HTTPException(status_code=409, detail="Already exists campaign with that name.")

    _bytes = file.file.read()

    validate_campaing_file(_bytes)

    background_tasks.add_task(insert_campaign, file=_bytes, campaign_name=campaign_name, api_token=pi_api_token)

@router.get("/campaign-status/{campaign}")
async def campaign_status(campaign: str, pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]) -> dict:
    redis_db = get_redis_db()

    client = ClientController.get_by_api_token(api_token=pi_api_token)

    key = f"LEAD-LOADING-{client.email}-{campaign}"

    data = redis_db.get(key)

    if data is None:
        raise fastapi.HTTPException(status_code=404)

    output =  json.loads(data)

    if output["status"] == "DONE":
        redis_db.delete(key)

    return output

def insert_campaign(campaign_name: str, file: bytes, api_token: pydantic.UUID4):
    redis_db = get_redis_db()

    client = ClientController.get_by_api_token(api_token=api_token)

    campaign = CampaignController.save(campaign=Campaign(owner=client.email, name=campaign_name, created_at=dt.datetime.now(), active=True))

    unipile_cfg: dict = APIConfig.get("Unipile")

    key = f"LEAD-LOADING-{client.email}-{campaign.name}"

    execution = dict(status="LOADING", progress=0.0)

    redis_db.set(key, json.dumps(execution))

    sheet = openpyxl.open(io.BytesIO(file))["Sheet"]

    rows = list(filter(any, list(sheet.iter_rows(min_row=2, values_only=True))))

    failed_leads: list[FailedLead] = list()

    i = 0

    unipile = UnipileService(authorization_key=unipile_cfg["AuthorizationKey"],
                             subdomain=unipile_cfg["Subdomain"],
                             port=unipile_cfg["Port"])

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
            else:
                ContactController.send_email_to_client(
                    subject="Prospector Inteligente: Falha ao carregar a campanha.",
                    message=f"Algo falhou ao carregar a campanha: '{campaign_name}'.\n"
                             "Por favor, tente novamente mais tarde ou entre em contato com o suporte.",
                    client=client
                )
                raise
        except:
            ContactController.send_email_to_client(
                subject="Prospector Inteligente: Falha ao carregar a campanha.",
                message=f"Algo falhou ao carregar a campanha: '{campaign_name}'.\n"
                         "Por favor, tente novamente mais tarde ou entre em contato com o suporte.",
                client=client
            )
            raise

        lead = Lead(campaign=campaign.id,
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

    if failed_leads:
        ContactController.send_email_to_client(
            subject=f"Prospector Inteligente - Falha ao carregar alguns contatos da campanha: '{campaign_name}'.",
            message="Mensagem automática:\n"
                    f"Não foi possível carregar todos os contatos da campanha: '{campaign_name}'.\n"
                    + f"\nNo total foram carregados {1.0 - (len(failed_leads) / len(rows))}% de todos os contatos.\n"
                    + "Os seguintes falharam:\n"
                    + '\n'.join([ f"{i + 1}) Nome: '{l.first_name} {l.last_name}' / Perfil: '{l.profile_url}'" for i, l in enumerate(failed_leads) ]),
            client=client
        )
    else:
        ContactController.send_email_to_client(
            subject=f"Prospector Inteligente - Campanha carregada com sucesso: '{campaign_name}'.",
            message=f"Mensagem automática: Todos os contatos foram carregado com sucesso.\n",
            client=client
        )

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

    lead_headline: str | None = linkedin_profile.get("headline")

    if lead_headline is None:
        raise ThirdPartyError(message="Linkedin profile retrieved from Unipile has no key: 'headline'.", context=linkedin_profile)

    extraction["lead_headline"] = lead_headline

    lead_contact_info: dict = linkedin_profile.get("contact_info", dict())

    extraction["emails"] = lead_contact_info.get("emails", list())
    extraction["phones"] = lead_contact_info.get("phones", list())

    return extraction
