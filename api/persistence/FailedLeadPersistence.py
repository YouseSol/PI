import logging

import psycopg2

from api.domain.FailedLead import FailedLead

from api.persistence.connector import get_postgres_db

from api.exception.APIException import APIException
from api.exception.InexistentObjectException import InexistentObjectException


logger = logging.getLogger(__name__)

class FailedLeadPersistence(object):

    @classmethod
    def save(cls, failed_lead: FailedLead) -> FailedLead:
        db = get_postgres_db()

        try:
            with db.cursor() as cursor:
                cursor.execute(
                    '''
                        INSERT INTO PI.FailedLead(
                            campaign,
                            first_name,
                            last_name,
                            profile_url
                        )
                        VALUES (%s, %s, %s, %s)
                        RETURNING *
                    ''',
                    (failed_lead.campaign,
                     failed_lead.first_name, failed_lead.last_name,
                     failed_lead.profile_url)
                )

                data: dict = cursor.fetchone()

                if data is None:
                    raise APIException(message="Database failed to insert and return data.", context=dict(table="FailedLead", operation="INSERT"))

                return FailedLead.model_validate(dict(data))
        except psycopg2.DatabaseError as e:
            db.rollback()

            raise

    @classmethod
    def get_by_id(cls, id: int) -> FailedLead:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM PI.FailedLead WHERE id = %s",
                (id, )
            )

            data: dict | None = cursor.fetchone()

            if data is None:
                raise InexistentObjectException(message=f"No failed lead with id: '{id}'.")

            return FailedLead.model_validate(dict(data))

    @classmethod
    def count(cls, campaign_id: int) -> int:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) as count FROM PI.FailedLead WHERE campaign = %s",
                (campaign_id, )
            )

            data: dict = cursor.fetchall()

            if data is None:
                raise APIException(message="Database failed to return data.", context=dict(table="FailedLead", operation="SELECT"))

            return data["count"]

    @classmethod
    def get(cls, campaign_id: int, page_size: int, page: int) -> list[FailedLead]:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM PI.FailedLead WHERE campaign = %s LIMIT %s OFFSET %s",
                (campaign_id, page_size, page * page_size)
            )

            data: list[dict] = cursor.fetchall()

            if data is None:
                raise APIException(message="Database failed to return data.", context=dict(table="FailedLead", operation="SELECT"))

            return [ FailedLead.model_validate(l) for l in data ]
