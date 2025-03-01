import pydantic

from api.domain.Campaign import Campaign
from api.domain.Lead import Lead


class CountResponse(pydantic.BaseModel):
    count: int

class LeadsResponse(pydantic.BaseModel):
    leads: list[Lead]

class CampaignsResponse(pydantic.BaseModel):
    campaigns: list[Campaign]
