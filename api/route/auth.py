import datetime as dt, json, logging, random, typing as t

import fastapi, pydantic

from api.route import dependencies

from appconfig.AppConfig import AppConfig

from api.domain.Client import LoginForm, RegisterForm, Client

from api.controller.Controller import Controller
from api.controller.ClientController import ClientController
from api.controller.ContactController import ContactController

from api.persistence.connector import get_redis_db

from api.exception.DuplicatingObjectException import DuplicatingObjectException
from api.exception.InexistentObjectException import InexistentObjectException


logger = logging.getLogger(__name__)

router = fastapi.APIRouter(prefix="/auth", tags=[ "Auth" ])

@router.post("/register")
async def register(form: RegisterForm) -> Client:
    try:
        system_client = ClientController.register(form)

        Controller.save()

        return Client(**system_client.dict(include=Client.__fields__.keys()))
    except DuplicatingObjectException:
        raise fastapi.exceptions.HTTPException(status_code=409, detail="Email already in use.")

@router.post("/login")
async def login(form: LoginForm) -> Client:
    system_client = ClientController.login(form)

    if system_client is not None:
        return Client(**system_client.dict(include=Client.__fields__.keys()))

    raise fastapi.exceptions.HTTPException(status_code=404, detail="Invalid email or password.")

class UpdatePasswordForm(pydantic.BaseModel):
    email: str
    old_password: str
    new_password: str

@router.post("/update-password", dependencies=[ fastapi.Depends(dependencies.has_valid_api_token) ])
async def update_password(form: UpdatePasswordForm, pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]) -> Client:
    system_client = ClientController.login(LoginForm(email=form.email, password=form.old_password))

    if system_client is None:
        raise fastapi.exceptions.HTTPException(status_code=404, detail="Invalid email or password.")

    if system_client.token != str(pi_api_token):
        raise fastapi.exceptions.HTTPException(status_code=401, detail="Unauthorized.")

    system_client = ClientController.update_password(client=system_client, password=form.new_password)

    Controller.save()

    return Client(**system_client.dict(include=Client.__fields__.keys()))

class GetResetPasswordBody(pydantic.BaseModel):
    email: str

@router.post("/reset-password")
async def start_reset_password(reset: GetResetPasswordBody):
    try:
        client = ClientController.get_by_email(email=reset.email)
    except InexistentObjectException:
        raise fastapi.exceptions.HTTPException(status_code=404, detail="Email not found.")

    redis = get_redis_db()

    key = f"RESET-PASSWORD-TOKEN-{client.email}"

    current_reset_password_state_str = redis.get(key)

    now = dt.datetime.now().timestamp()

    if current_reset_password_state_str is not None:
        current_reset_password_state = json.loads(str(current_reset_password_state_str))

        if now - current_reset_password_state["timestamp"] >= AppConfig["ResetPasswordCodeValidationTimeInSeconds"]:
            raise fastapi.HTTPException(status_code=409, detail="Still exists a valid reset code for that account.")

    code = "".join([ str(random.randint(0, 9)) for _ in range(6) ])

    redis.set(key, json.dumps(dict(code=code, timestamp=now)))

    ContactController.send_email_to_client(
        client=client,
        subject="[PI] Código para resetar a sua senha.",
        body=f"O código para resetar a sua senha é: '{code}'.\n"
              "Caso você não tenha acionado a função de resetar sua senha, por favor, ignore este email."
    )

class PostResetPasswordBody(pydantic.BaseModel):
    email: str
    code: int
    new_password: str

@router.put("/reset-password")
async def finish_reset_password(reset: PostResetPasswordBody) -> Client:
    try:
        client = ClientController.get_by_email(email=reset.email)
    except InexistentObjectException:
        raise fastapi.exceptions.HTTPException(status_code=404, detail="Email not found.")

    redis = get_redis_db()

    key = f"RESET-PASSWORD-TOKEN-{client.email}"

    current_reset_password_state_str = redis.get(key)

    if current_reset_password_state_str is None:
        raise fastapi.HTTPException(status_code=409, detail="Do not exists a valid reset code for that account.")

    current_reset_password_state = json.loads(str(redis.get(key)))

    if int(current_reset_password_state["code"]) != reset.code:
        raise fastapi.HTTPException(status_code=401, detail="Invalid code.")

    client = ClientController.update_password(client=client, password=reset.new_password)

    Controller.save()

    redis.delete(f"RESET-PASSWORD-TOKEN-{client.email}")

    return Client(**client.dict(include=Client.__fields__.keys()))
