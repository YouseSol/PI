import logging

import fastapi

from api.controller.Controller import Controller
from api.controller.ClientController import ClientController

from api.domain.Client import LoginForm, RegisterForm, Client

from api.exception.DuplicatingObjectException import DuplicatingObjectException


logger = logging.getLogger(__name__)

router = fastapi.APIRouter(prefix="/auth", tags=[ "Users" ])

@router.post("/register", status_code=201)
async def register(form: RegisterForm) -> Client:
    try:
        system_client = ClientController.register(form)

        Controller.save()

        return Client(**system_client.dict(include=Client.__fields__.keys()))
    except DuplicatingObjectException:
        raise fastapi.exceptions.HTTPException(status_code=409, detail="Email already in use.")

@router.post("/login", status_code=201)
async def login(form: LoginForm) -> Client:
    system_client = ClientController.login(form)

    if system_client is not None:
        return Client(**system_client.dict(include=Client.__fields__.keys()))

    raise fastapi.exceptions.HTTPException(status_code=404, detail="Invalid email or password.")
