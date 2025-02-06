import logging

import pydantic

from api.domain.SalesRepresentative import SalesRepresentative
from api.persistence.SalesRepresentativePersistence import SalesRepresentativePersistence


logger = logging.getLogger(__name__)

class SalesRepresentativeController(object):

    @classmethod
    def save(cls, sales_representative: SalesRepresentative) -> SalesRepresentative:
        return SalesRepresentativePersistence.save(sales_representative=sales_representative)

    @classmethod
    def get(cls, owner: str) -> SalesRepresentative:
        return SalesRepresentativePersistence.get(owner=owner)
