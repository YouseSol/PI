import datetime as dt

import pydantic


class LoginForm(pydantic.BaseModel):
    email: str
    password: str

class UserInfo(pydantic.BaseModel):
    first_name: str
    last_name: str
    standard_message: str

class RegisterForm(LoginForm, UserInfo):
    linkedin_account_id: str
    pass

class Client(UserInfo):
    email: str
    active: bool
    token: str

class SystemClient(Client):
    linkedin_account_id: str
    hash: str

    token: str

    created_at: dt.datetime

    deleted: bool
    deleted_at: dt.datetime | None = None

    def is_an_appropriate_time_to_answer(self) -> bool:
        now = dt.datetime.now()
        return now.hour >= 11 and now.hour < 22 # INFO: America/Sao_Paulo 8 - 18
