import datetime as dt, logging

from api.domain.Client import SystemClient
from api.domain.Lead import Lead, SystemLead
from api.domain.Campaign import Campaign, SystemCampaign

from api.persistence.LeadPersistence import LeadPersistence


logger = logging.getLogger(__name__)

class LeadController(object):

    @classmethod
    def save(cls, lead: SystemLead) -> SystemLead:
        return LeadPersistence.save(lead=lead)

    @classmethod
    def delete(cls, lead: SystemLead):
        lead.deleted = True
        lead.deleted_at = dt.datetime.now()
        LeadPersistence.save(lead=lead)

    @classmethod
    def is_a_valid_lead(cls, client: SystemClient, linkedin_public_identifier: str) -> bool:
        return LeadPersistence.is_a_valid_lead(client=client, linkedin_public_identifier=linkedin_public_identifier)

    @classmethod
    def get_by_linkedin_public_identifier(cls, client: SystemClient, linkedin_public_identifier: str) -> SystemLead:
        return LeadPersistence.get_by_linkedin_public_identifier(client=client, linkedin_public_identifier=linkedin_public_identifier)

    @classmethod
    def get_by_id(cls, client: SystemClient, id: int) -> SystemLead:
        return LeadPersistence.get_by_id(client=client, id=id)

    @classmethod
    def count_client_leads(cls, client: SystemClient) -> int:
        return LeadPersistence.count_client_leads(client=client)

    @classmethod
    def paginate_client_leads(cls, client: SystemClient, page_size: int, page: int) -> list[SystemLead]:
        return LeadPersistence.paginate_client_leads(client=client, page_size=page_size, page=page)

    @classmethod
    def count_leads_in_campaign(cls, campaign: SystemCampaign) -> int:
        return LeadPersistence.count_leads_in_campaign(campaign=campaign)

    @classmethod
    def paginate_leads_in_campaign(cls,
                              campaign: SystemCampaign,
                              query: str | None,
                              has_conversation: bool | None, is_active: bool | None,
                              page: int, page_size: int) -> list[SystemLead]:
        return LeadPersistence.paginate_leads_in_campaign(
            campaign=campaign,
            query= str() if query == None else query,
            has_conversation=has_conversation, is_active=is_active,
            page=page, page_size=page_size
        )
