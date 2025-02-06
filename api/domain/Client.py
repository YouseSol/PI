import datetime as dt

import pydantic


class LoginForm(pydantic.BaseModel):
    email: str
    password: str

class UserInfo(pydantic.BaseModel):
    first_name: str
    last_name: str
    linkedin_account_id: str
    standart_message: str

class RegisterForm(LoginForm, UserInfo):
    pass

class Client(UserInfo):
    email: str
    active: bool
    token: str

class SystemClient(Client):
    hash: str

    token: str

    created_at: dt.datetime

    deleted: bool
    deleted_at: dt.datetime | None = None
