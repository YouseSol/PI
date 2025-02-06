import logging

import psycopg2

import pydantic

from api.persistence.connector import get_postgres_db

from api.exception.APIException import APIException
from api.exception.InexistentObjectException import InexistentObjectException

from api.domain.SalesRepresentative import SalesRepresentative


logger = logging.getLogger(__name__)

class SalesRepresentativePersistence(object):

    @classmethod
    def save(cls, sales_representative: SalesRepresentative) -> SalesRepresentative:
        db = get_postgres_db()

        try:
            with db.cursor() as cursor:
                cursor.execute(
                    '''
                        INSERT INTO PI.SalesRepresentative(
                            client,
                            first_name,
                            last_name,
                            email,
                            active,
                            deleted,
                            deleted_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING *
                    ''',
                    (sales_representative.client,
                     sales_representative.first_name,
                     sales_representative.last_name,
                     sales_representative.email,
                     sales_representative.active,
                     sales_representative.deleted,
                     sales_representative.deleted_at)
                )

                data: dict = cursor.fetchone()

                if data is None:
                    raise APIException(message="Database failed to insert and return data.", context=dict(table="SalesRepresentative", operation="INSERT"))

                return SalesRepresentative.model_validate(dict(data))
        except psycopg2.DatabaseError as e:
            db.rollback()

            raise

    @classmethod
    def get(cls, owner: str) -> SalesRepresentative:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM PI.SalesRepresentative WHERE owner = %s AND deleted = false",
                (owner, )
            )

            data: dict = cursor.fetchone()

            if data is None:
                raise InexistentObjectException(message=f"No sales representative registered for account: '{owner}'.")

            return SalesRepresentative.model_validate(data)
