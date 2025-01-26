import logging, typing as t, zipfile

import fastapi
import pydantic

import openpyxl

from api.APIConfig import APIConfig

from api.controller.ClientController import ClientController
from api.controller.Controller import Controller
from api.controller.LeadController import LeadController
from api.exception.APIException import APIException
from api.exception.ThirdPartyError import ThirdPartyError

from api.thirdparty.UnipileService import UnipileService

from api.domain.Client import Client
from api.domain.Lead import Lead


logger = logging.getLogger(__name__)

router = fastapi.APIRouter(prefix="/alessia", tags=[ "Alessia" ])


@router.post("/activate-leads")
async def activate_leads(file: fastapi.UploadFile, pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]):
    validate_campaing_file(file.file)

    sheet = openpyxl.open(file.file)["Sheet"]

    client = ClientController.get_by_api_token(api_token=pi_api_token)

    unipile_cfg: dict = APIConfig.get("Unipile")

    unipile = UnipileService(authorization_key=unipile_cfg["AuthorizationKey"],
                             subdomain=unipile_cfg["Subdomain"],
                             port=unipile_cfg["Port"])

    for row in sheet.iter_rows(min_row=2, values_only=True):
        logger.debug(row)

        lead_linkedin_url = str(row[8])

        lead_account_id = lead_linkedin_url.split("/")[-1]

        # INFO: This call can fail and we dont know why. Occured for a specific profile. Maybe privace involved.
        lead_linkedin_profile: dict = extract_data_from_unipile_retrieve_profile(
            linkedin_profile=unipile.retrieve_profile(account_retrieving=client.linkedin_account_id, account_id=lead_account_id)
        )

        lead = Lead(owner=client.email,
                    linkedin_public_identifier=lead_linkedin_profile["linkedin_identifier"],
                    first_name=lead_linkedin_profile["first_name"],
                    last_name=lead_linkedin_profile["last_name"],
                    emails=lead_linkedin_profile["emails"],
                    phones=lead_linkedin_profile["phones"],
                    active=True,
                    deleted=False,
                    chat_id=None)

        LeadController.save(lead)

    Controller.save()


@router.post("/deactivate-leads")
async def deactivate_leads(file: fastapi.UploadFile, pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]):
    validate_campaing_file(file.file)

    sheet = openpyxl.open(file.file)["Sheet"]

    client = ClientController.get_by_api_token(api_token=pi_api_token)

    unipile_cfg: dict = APIConfig.get("Unipile")

    unipile = UnipileService(authorization_key=unipile_cfg["AuthorizationKey"],
                             subdomain=unipile_cfg["Subdomain"],
                             port=unipile_cfg["Port"])

    for row in sheet.iter_rows(min_row=2, values_only=True):
        lead_linkedin_url = str(row[8])

        lead_account_id = lead_linkedin_url.split("/")[-1]

        # INFO: This call can fail and we dont know why. Occured for a specific profile. Maybe privace involved.
        lead_linkedin_profile: dict = extract_data_from_unipile_retrieve_profile(
            linkedin_profile=unipile.retrieve_profile(account_retrieving=client.linkedin_account_id, account_id=lead_account_id)
        )

        lead = Lead(owner=client.email,
                    linkedin_public_identifier=lead_linkedin_profile["linkedin_identifier"],
                    first_name=lead_linkedin_profile["first_name"],
                    last_name=lead_linkedin_profile["last_name"],
                    emails=lead_linkedin_profile["emails"],
                    phones=lead_linkedin_profile["phones"],
                    active=True,
                    deleted=False)

        LeadController.save(lead)

    Controller.save()

def validate_campaing_file(file: t.BinaryIO):
    try:
        sheet = openpyxl.open(file)["Sheet"]
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
    logger.debug(linkedin_profile)

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

    extraction["last_headline"] = lead_headline

    lead_contact_info: dict = linkedin_profile.get("contact_info", dict())

    extraction["emails"] = lead_contact_info.get("emails", list())
    extraction["phones"] = lead_contact_info.get("phones", list())

    return extraction
