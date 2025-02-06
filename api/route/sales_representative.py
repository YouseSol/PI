import logging, typing as t, datetime as dt

import fastapi, pydantic

from api.APIConfig import APIConfig

from api.controller.SalesRepresentativeController import SalesRepresentativeController
from api.domain.SalesRepresentative import SalesRepresentative

from api.controller.Controller import Controller
from api.controller.ClientController import ClientController
from api.controller.LeadController import LeadController

from api.thirdparty.UnipileService import UnipileService


logger = logging.getLogger(__name__)

router = fastapi.APIRouter(prefix="/sales-representative", tags=[ "Leads" ])

@router.post("/")
async def post(sales_representative: SalesRepresentative, pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]) -> SalesRepresentative:
    client = ClientController.get_by_api_token(api_token=pi_api_token)

    sr =  SalesRepresentativeController.save(sales_representative=sales_representative)

    Controller.save()

    return sr
