import logging, typing as t

import fastapi, pydantic

from api.controller.Controller import Controller
from api.controller.ClientController import ClientController

from api.domain.Client import Client

from api.exception.DuplicatingObjectException import DuplicatingObjectException


logger = logging.getLogger(__name__)

router = fastapi.APIRouter(prefix="/user", tags=[ "Users" ])

@router.post("/activate")
async def activate(pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]) -> Client:
    system_client = ClientController.get_by_api_token(api_token=pi_api_token)

    system_client.active = True

    ClientController.set_active(api_token=pi_api_token, active=True)

    Controller.save()

    return Client(**system_client.dict(include=Client.__fields__.keys()))


@router.post("/deactivate")
async def deactivate(pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]) -> Client:
    system_client = ClientController.get_by_api_token(api_token=pi_api_token)

    system_client.active = False

    ClientController.set_active(api_token=pi_api_token, active=False)

    Controller.save()

    return Client(**system_client.dict(include=Client.__fields__.keys()))
