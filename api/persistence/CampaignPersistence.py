import datetime as dt, logging

import psycopg2

from api.domain.Campaign import Campaign, SystemCampaign
from api.domain.Client import SystemClient
from api.domain.Lead import SystemLead

from api.persistence.connector import get_postgres_db

from api.exception.APIException import APIException
from api.exception.InexistentObjectException import InexistentObjectException


logger = logging.getLogger(__name__)

class CampaignPersistence(object):

    @classmethod
    def save(cls, campaign: SystemCampaign) -> SystemCampaign:
        db = get_postgres_db()

        with db.cursor() as cursor:
            try:
                cursor.execute(
                    '''
                        INSERT INTO PI.Campaign(
                            owner,
                            name,
                            created_at,
                            active,
                            deleted,
                            deleted_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING *
                    ''',
                    (campaign.owner,
                     campaign.name,
                     campaign.created_at,
                     campaign.active,
                     campaign.deleted,
                     campaign.deleted_at)
                )
            except psycopg2.errors.UniqueViolation:
                db.rollback()

                cursor.execute(
                    '''
                        UPDATE PI.Campaign
                        SET created_at = %s,
                            active = %s,
                            deleted = %s,
                            deleted_at = %s,
                        WHERE name = %s AND owner = %s AND deleted = FALSE
                        RETURNING *
                    ''',
                    (campaign.created_at,
                     campaign.active,
                     campaign.deleted, campaign.deleted_at,
                     campaign.name, campaign.owner)
                )
            except psycopg2.DatabaseError as e:
                db.rollback()
                raise

            data: dict = cursor.fetchone()

            if data is None:
                raise APIException(message="Database failed to insert and return data.", context=dict(table="Campaign", operation="INSERT"))

            return SystemCampaign.model_validate(dict(data))

    @classmethod
    def update_name(cls, campaign: SystemCampaign, new_name: str) -> SystemCampaign:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                '''
                UPDATE PI.Campaign
                SET name = %s
                WHERE owner = %s AND name = %s AND deleted = false
                RETURNING *
                ''',
                (new_name, campaign.owner, campaign.name)
            )

            data: dict = cursor.fetchone()

            if data is None:
                raise InexistentObjectException(message=f"No campaign named '{campaign.name}' for owner '{campaign.owner}'.")

            logger.debug(data)

            return SystemCampaign.model_validate(data)

    @classmethod
    def get_by_name(cls, client: SystemClient, name: str) -> SystemCampaign:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM PI.Campaign WHERE owner = %s AND name = %s AND deleted = false",
                (client.email, name)
            )

            data: dict = cursor.fetchone()

            if data is None:
                raise InexistentObjectException(message=f"No campaign named '{name}' for owner '{owner}'.")

            return SystemCampaign.model_validate(data)

    @classmethod
    def get_by_id(cls, client: SystemClient, id: int) -> SystemCampaign:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM PI.Campaign WHERE owner = %s AND id = %s AND deleted = false",
                (client.email, id)
            )

            data: dict = cursor.fetchone()

            if data is None:
                raise InexistentObjectException(message=f"No campaign with id '{name}' for owner '{owner}'.")

            return SystemCampaign.model_validate(data)

    @classmethod
    def count(cls, client: SystemClient) -> int:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) as count FROM PI.Campaign WHERE owner = %s AND deleted = false",
                (client.email, )
            )

            data: dict = cursor.fetchall()

            if data is None:
                raise APIException(message="Database failed to return data.", context=dict(table="Campaign", operation="SELECT"))

            return data["count"]

    @classmethod
    def paginate(cls, client: SystemClient, page_size: int, page: int) -> list[SystemCampaign]:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM PI.Campaign WHERE owner = %s AND deleted = false LIMIT %s OFFSET %s",
                (client.email, page_size, page * page_size)
            )

            data: list[dict] = cursor.fetchall()

            if data is None:
                raise APIException(message="Database failed to return data.", context=dict(table="Campaign", operation="SELECT"))

            return [ SystemCampaign.model_validate(c) for c in data ]

    @classmethod
    def get_all(cls, client: SystemClient) -> list[SystemCampaign]:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM PI.Campaign WHERE owner = %s AND deleted = false",
                (client.email, )
            )

            data: list[dict] = cursor.fetchall()

            logger.debug(data)

            if data is None:
                raise APIException(message="Database failed to return data.", context=dict(table="Campaign", operation="SELECT"))

            return [ SystemCampaign.model_validate(c) for c in data ]

    @classmethod
    def exists(cls, name: str, client: SystemClient) -> bool:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) as count FROM PI.Campaign WHERE owner = %s AND name = %s AND deleted = false",
                (client.email, name)
            )

            data: dict = cursor.fetchone()

            if data is None:
                raise APIException(message="Database failed to return data.", context=dict(table="Campaign", operation="SELECT"))

            return data["count"] == 1

    @classmethod
    def count_answered_chats(cls, campaign: SystemCampaign) -> int:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                """
                    SELECT COUNT(DISTINCT l.id) AS count
                    FROM
                        PI.Campaign c
                        JOIN PI.Lead l ON c.id = l.campaign
                        JOIN PI.MessageSent m ON l.id = m.lead
                    WHERE c.id = %s
                """,
                (campaign.id, )
            )

            data: dict = cursor.fetchone()

            if data is None:
                raise APIException(message="Database failed to return data.", context=dict(table="Campaign", operation="SELECT"))

            return data["count"]

    @classmethod
    def count_messages_per_day(cls, campaign: SystemCampaign, since: dt.date, before: dt.date) -> list[dict]:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                """
                SELECT DATE(m.sent_at) AS date, COUNT(DISTINCT m.id) AS messages_sent
                FROM
                    PI.Campaign c
                    JOIN PI.Lead l ON c.id = l.campaign
                    JOIN PI.MessageSent m ON l.id = m.lead
                WHERE c.id = %s AND DATE(m.sent_at) >= %s AND DATE(m.sent_at) <= %s
                GROUP BY DATE(m.sent_at)
                """,
                (campaign.id, since, before)
            )

            data: list[dict[str, dt.date | int]] = cursor.fetchall()

            if data is None:
                raise APIException(message="Database failed to return data.", context=dict(table="Campaign", operation="SELECT"))

            return data
