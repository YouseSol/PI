import datetime as dt, logging

from api.domain.Client import SystemClient
from api.domain.Campaign import SystemCampaign
from api.domain.Lead import SystemLead

from api.persistence.CampaignPersistence import CampaignPersistence


logger = logging.getLogger(__name__)

class CampaignController(object):

    @classmethod
    def save(cls, campaign: SystemCampaign) -> SystemCampaign:
        return CampaignPersistence.save(campaign=campaign)

    @classmethod
    def update_name(cls, campaign: SystemCampaign, new_name: str) -> SystemCampaign:
        return CampaignPersistence.update_name(campaign=campaign, new_name=new_name)

    @classmethod
    def delete(cls, campaign: SystemCampaign):
        campaign.deleted = True
        campaign.deleted_at = dt.datetime.now()
        CampaignPersistence.save(campaign=campaign)

    @classmethod
    def get_all(cls, client: SystemClient) -> list[SystemCampaign]:
        return CampaignPersistence.get_all(client=client)

    @classmethod
    def count(cls, client: SystemClient) -> int:
        return CampaignPersistence.count(client=client)

    @classmethod
    def count_answered_chats(cls, campaign: SystemCampaign) -> int:
        return CampaignPersistence.count_answered_chats(campaign=campaign)

    @classmethod
    def count_messages_per_day(cls, campaign: SystemCampaign, since: dt.date, before: dt.date) -> list[dict]:
        return CampaignPersistence.count_messages_per_day(campaign=campaign, since=since, before=before)

    @classmethod
    def paginate(cls, client: SystemClient, page_size: int, page: int) -> list[SystemCampaign]:
        return CampaignPersistence.paginate(client=client, page_size=page_size, page=page)

    @classmethod
    def get_by_name(cls, client: SystemClient, name: str) -> SystemCampaign:
        return CampaignPersistence.get_by_name(client=client, name=name)

    @classmethod
    def get_by_id(cls, client: SystemClient, id: int) -> SystemCampaign:
        return CampaignPersistence.get_by_id(client=client, id=id)

    @classmethod
    def exists(cls, client: SystemClient, name: str) -> bool:
        return CampaignPersistence.exists(client=client, name=name)
