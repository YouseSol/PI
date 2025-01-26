import pydantic


class Lead(pydantic.BaseModel):
    owner: str

    id: int = 0

    linkedin_public_identifier: str
    chat_id: str | None

    first_name: str
    last_name: str

    emails: list[str]
    phones: list[str]

    active: bool = True
    deleted: bool = False
