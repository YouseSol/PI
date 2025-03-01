import datetime as dt

import pydantic


class MessageSent(pydantic.BaseModel):
    id: str
    lead: int
    sent_at: dt.datetime
    feedback: str | None = None
