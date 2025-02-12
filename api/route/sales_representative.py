import datetime as dt, logging, typing as t

import fastapi, pydantic

from appconfig import AppConfig

from api.domain.SalesRepresentative import SalesRepresentative

from api.controller.Controller import Controller
from api.controller.ClientController import ClientController
from api.controller.SalesRepresentativeController import SalesRepresentativeController
from api.controller.LeadController import LeadController


logger = logging.getLogger(__name__)

router = fastapi.APIRouter(prefix="/sales-representative", tags=[ "SalesRepresentative" ])

@router.post("/")
async def post(sales_representative: SalesRepresentative, pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]) -> SalesRepresentative:
    client = ClientController.get_by_api_token(api_token=pi_api_token)

    sr =  SalesRepresentativeController.save(sales_representative=sales_representative)

    Controller.save()

    return sr
