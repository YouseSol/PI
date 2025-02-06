import datetime as dt

import pydantic


class Lead(pydantic.BaseModel):
    campaign: int

    id: int = 0

    linkedin_public_identifier: str
    chat_id: str | None = None

    first_name: str
    last_name: str

    emails: list[str]
    phones: list[str]

    active: bool = True

    deleted: bool = False
    deleted_at: dt.datetime | None = None
