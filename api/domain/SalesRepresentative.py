import datetime as dt

import pydantic


class SalesRepresentative(pydantic.BaseModel):
    client: str

    first_name: str
    last_name: str

    email: str

    active: bool = True

    deleted: bool = False
    deleted_at: dt.datetime | None = None
