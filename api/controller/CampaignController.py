import logging

import pydantic

from api.domain.Campaign import Campaign

from api.persistence.CampaignPersistence import CampaignPersistence

logger = logging.getLogger(__name__)


class CampaignController(object):

    @classmethod
    def save(cls, campaign: Campaign) -> Campaign:
        return CampaignPersistence.save(campaign=campaign)

    @classmethod
    def count(cls, owner: str) -> int:
        return CampaignPersistence.count(owner=owner)

    @classmethod
    def get(cls, owner: str, page_size: int, page: int) -> list[Campaign]:
        return CampaignPersistence.get(owner=owner, page_size=page_size, page=page)

    @classmethod
    def get_by_name(cls, name: str, owner: str) -> Campaign:
        return CampaignPersistence.get_by_name(name=name, owner=owner)

    @classmethod
    def get_by_id(cls, id: int, owner: str) -> Campaign:
        return CampaignPersistence.get_by_id(id=id, owner=owner)

    @classmethod
    def exists(cls, name: str, owner: str) -> bool:
        return CampaignPersistence.exists(name=name, owner=owner)
