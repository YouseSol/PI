import pydantic


class FailedLead(pydantic.BaseModel):
    campaign: int

    id: int = 0

    first_name: str
    last_name: str
    profile_url: str
