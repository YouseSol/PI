import datetime as dt, logging

from api.domain.Lead import Lead

from api.persistence.LeadPersistence import LeadPersistence


logger = logging.getLogger(__name__)

class LeadController(object):

    @classmethod
    def get(cls, owner: str, page_size: int, page: int) -> list[Lead]:
        return LeadPersistence.get(owner=owner, page_size=page_size, page=page)

    @classmethod
    def save(cls, lead: Lead) -> Lead:
        return LeadPersistence.save(lead=lead)

    @classmethod
    def delete(cls, lead: Lead) -> Lead:
        lead.deleted = True
        lead.deleted_at = dt.datetime.now()
        return LeadPersistence.save(lead=lead)

    @classmethod
    def is_a_valid_lead(cls, owner: str, linkedin_public_identifier: str):
        return LeadPersistence.is_a_valid_lead(owner=owner, linkedin_public_identifier=linkedin_public_identifier)

    @classmethod
    def get_by_owner_and_linkedin_public_identifier(cls, owner: str, linkedin_public_identifier: str) -> Lead:
        return LeadPersistence.get_by_owner_and_linkedin_public_identifier(owner=owner, linkedin_public_identifier=linkedin_public_identifier)

    @classmethod
    def get_by_id(cls, owner: str, id: int) -> Lead:
        return LeadPersistence.get_by_id(owner=owner, id=id)
