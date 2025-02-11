import logging

from api.domain.FailedLead import FailedLead

from api.persistence.FailedLeadPersistence import FailedLeadPersistence


logger = logging.getLogger(__name__)

class FailedLeadController(object):

    @classmethod
    def save(cls, failed_lead: FailedLead) -> FailedLead:
        return FailedLeadPersistence.save(failed_lead=failed_lead)

    @classmethod
    def get_by_id(cls, id: int) -> FailedLead:
        return FailedLeadPersistence.get_by_id(id=id)

    @classmethod
    def count(cls, campaign_id: int) -> int:
        return FailedLeadPersistence.count(campaign_id=campaign_id)

    @classmethod
    def get(cls, campaign_id: int, page_size: int, page: int) -> list[FailedLead]:
        return FailedLeadPersistence.get(campaign_id=campaign_id, page_size=page_size, page=page)
