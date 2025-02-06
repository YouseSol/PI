import datetime as dt

import pydantic


class Campaign(pydantic.BaseModel):
    id: int = 0

    owner: str

    name: str

    created_at: dt.datetime
    active: bool

    deleted: bool = False
    deleted_at: dt.datetime | None = None
