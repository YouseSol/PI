import pydantic


class Lead(pydantic.BaseModel):
    owner: str
    linkedin_public_identifier: str

    first_name: str
    last_name: str

    emails: list[str]
    phones: list[str]

    active: bool = True
    deleted: bool = False
