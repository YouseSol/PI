import logging, typing as t

import fastapi, pydantic

from api.route.responses import CountResponse, LeadsResponse

from api.domain.Client import Client
from api.domain.Lead import Lead

from api.controller.Controller import Controller
from api.controller.ClientController import ClientController
from api.controller.LeadController import LeadController

from api.exception.DuplicatingObjectException import DuplicatingObjectException


logger = logging.getLogger(__name__)

router = fastapi.APIRouter(prefix="/user", tags=[ "Users" ])

@router.post("/activate")
async def activate(pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]) -> Client:
    system_client = ClientController.get_by_api_token(api_token=pi_api_token)

    system_client.active = True

    ClientController.set_active(client=system_client, active=True)

    Controller.save()

    return Client(**system_client.dict(include=Client.__fields__.keys()))

@router.post("/deactivate")
async def deactivate(pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]) -> Client:
    system_client = ClientController.get_by_api_token(api_token=pi_api_token)

    system_client.active = False

    ClientController.set_active(client=system_client, active=False)

    Controller.save()

    return Client(**system_client.dict(include=Client.__fields__.keys()))

@router.get("/leads/count")
async def count_leads(pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]) -> CountResponse:
    client = ClientController.get_by_api_token(api_token=pi_api_token)

    return CountResponse(count=LeadController.count_client_leads(client=client))

@router.get("/leads")
async def paginate_leads(page_size: int, page: int,
                         pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]) -> LeadsResponse:
    client = ClientController.get_by_api_token(api_token=pi_api_token)

    leads = LeadController.paginate_client_leads(client=client, page_size=page_size, page=page)

    return LeadsResponse(leads=[ Lead(**system_lead.dict(include=Lead.__fields__.keys())) for system_lead in leads ])
