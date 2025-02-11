import logging

import psycopg2

from api.domain.Campaign import Campaign

from api.persistence.connector import get_postgres_db

from api.exception.APIException import APIException
from api.exception.InexistentObjectException import InexistentObjectException


logger = logging.getLogger(__name__)

class CampaignPersistence(object):

    @classmethod
    def save(cls, campaign: Campaign) -> Campaign:
        db = get_postgres_db()

        try:
            with db.cursor() as cursor:
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

                data: dict = cursor.fetchone()

                if data is None:
                    raise APIException(message="Database failed to insert and return data.", context=dict(table="Campaign", operation="INSERT"))

                return Campaign.model_validate(dict(data))
        except psycopg2.DatabaseError as e:
            db.rollback()

            raise

    @classmethod
    def get_by_name(cls, owner: str, name: str) -> Campaign:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM PI.Campaign WHERE owner = %s AND name = %s AND deleted = false",
                (owner, name)
            )

            data: dict = cursor.fetchone()

            if data is None:
                raise InexistentObjectException(message=f"No campaign named '{name}' for owner '{owner}'.")

            return Campaign.model_validate(data)

    @classmethod
    def get_by_id(cls, owner: str, id: int) -> Campaign:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM PI.Campaign WHERE owner = %s AND id = %s AND deleted = false",
                (owner, id)
            )

            data: dict = cursor.fetchone()

            if data is None:
                raise InexistentObjectException(message=f"No campaign with id '{name}' for owner '{owner}'.")

            return Campaign.model_validate(data)

    @classmethod
    def count(cls, owner: str) -> int:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) as count FROM PI.Campaign WHERE owner = %s AND deleted = false",
                (owner, )
            )

            data: dict = cursor.fetchall()

            if data is None:
                raise APIException(message="Database failed to return data.", context=dict(table="Campaign", operation="SELECT"))

            return data["count"]

    @classmethod
    def get(cls, owner: str, page_size: int, page: int) -> list[Campaign]:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM PI.Campaign WHERE owner = %s AND deleted = false LIMIT %s OFFSET %s",
                (owner, page_size, page * page_size)
            )

            data: list[dict] = cursor.fetchall()

            if data is None:
                raise APIException(message="Database failed to return data.", context=dict(table="Campaign", operation="SELECT"))

            return [ Campaign.model_validate(c) for c in data ]

    @classmethod
    def exists(cls, name: str, owner: str) -> bool:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) as count FROM PI.Campaign WHERE owner = %s AND name = %s AND deleted = false",
                (owner, name)
            )

            data: dict = cursor.fetchone()

            if data is None:
                raise APIException(message="Database failed to return data.", context=dict(table="Campaign", operation="SELECT"))

            return data["count"] == 1
