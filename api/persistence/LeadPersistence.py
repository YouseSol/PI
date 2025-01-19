import logging

import psycopg2

import pydantic

from api.persistence.connector import get_postgres_db

from api.exception.APIException import APIException
from api.exception.DuplicatingObjectException import DuplicatingObjectException
from api.exception.InexistentObjectException import InexistentObjectException

from api.domain.Lead import Lead


logger = logging.getLogger(__name__)

class LeadPersistence(object):

    @classmethod
    def save(cls, lead: Lead) -> Lead:
        db = get_postgres_db()

        try:
            with db.cursor() as cursor:
                cursor.execute(
                    '''
                        INSERT INTO PI.Lead(
                            owner,
                            linkedin_public_identifier,
                            first_name,
                            last_name,
                            emails,
                            phones,
                            active,
                            deleted
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (owner, linkedin_public_identifier)
                        DO UPDATE SET
                            first_name = EXCLUDED.first_name,
                            last_name = EXCLUDED.last_name,
                            emails = EXCLUDED.emails,
                            phones = EXCLUDED.phones,
                            active = EXCLUDED.active,
                            deleted = EXCLUDED.deleted
                        RETURNING *
                    ''',
                    (lead.owner, lead.linkedin_public_identifier,
                     lead.first_name, lead.last_name,
                     lead.emails, lead.phones,
                     lead.active, lead.deleted)
                )

                data: dict = cursor.fetchone()

                if data is None:
                    raise APIException(message="Database failed to insert and return data.", context=dict(table="Lead", operation="INSERT"))

                return Lead.model_validate(dict(data))
        except psycopg2.DatabaseError as e:
            db.rollback()

            raise

    @classmethod
    def is_a_valid_lead(cls, owner: str, linkedin_public_identifier: str) -> bool:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM PI.Lead WHERE owner = %s AND linkedin_public_identifier = %s AND deleted = false",
                (owner, linkedin_public_identifier)
            )

            return cursor.fetchone() is not None

    @classmethod
    def get_by_owner_and_linkedin_public_identifier(cls, owner: str, linkedin_public_identifier: str) -> Lead:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM PI.Lead WHERE owner = %s AND linkedin_public_identifier = %s",
                (owner, linkedin_public_identifier)
            )

            data: dict = cursor.fetchone()

            if data is None:
                raise InexistentObjectException(message=f"No lead with owner and linkedin_public_identifier: '{(owner, linkedin_public_identifier)}'.")

            return Lead.model_validate(dict(data))
