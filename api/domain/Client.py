import pydantic


class LoginForm(pydantic.BaseModel):
    email: str
    password: str

class UserInfo(pydantic.BaseModel):
    first_name: str
    last_name: str | None
    linkedin_account_id: str

class RegisterForm(LoginForm, UserInfo):
    pass

class Client(UserInfo):
    email: str
    active: bool
    token: str

class SystemClient(Client):
    hash: str
    deleted: bool
    token: str
