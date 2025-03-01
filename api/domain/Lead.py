import datetime as dt

import pydantic


class Lead(pydantic.BaseModel):
    id: int = 0

    first_name: str
    last_name: str

    emails: list[str] = list()
    phones: list[str] = list()

    feedback: bool | None = None

    active: bool = True

class SystemLead(Lead):
    campaign: int

    linkedin_public_identifier: str
    chat_id: str | None = None

    deleted: bool = False
    deleted_at: dt.datetime | None = None
