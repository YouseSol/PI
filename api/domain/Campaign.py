import datetime as dt

import pydantic


class Campaign(pydantic.BaseModel):
    id: int = 0

    name: str

    active: bool

class SystemCampaign(Campaign):
    owner: str

    created_at: dt.datetime

    deleted: bool = False
    deleted_at: dt.datetime | None = None
