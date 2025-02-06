import datetime as dt

import pydantic


class SalesRepresentative(pydantic.BaseModel):
    id: int

    owner: str

    first_name: str
    last_name: str

    email: str

    active: bool = True

    created_at: dt.datetime

    deleted: bool = False
    deleted_at: dt.datetime | None = None
