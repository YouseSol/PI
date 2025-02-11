import logging

import psycopg2

from api.domain.Lead import Lead

from api.persistence.connector import get_postgres_db

from api.controller.ClientController import ClientController

from api.exception.APIException import APIException
from api.exception.InexistentObjectException import InexistentObjectException


logger = logging.getLogger(__name__)

class LeadPersistence(object):

    @classmethod
    def save(cls, lead: Lead) -> Lead:
        db = get_postgres_db()

        try:
            with db.cursor() as cursor:
                try:
                    cursor.execute(
                        '''
                            INSERT INTO PI.Lead(
                                campaign,
                                linkedin_public_identifier,
                                chat_id,
                                first_name,
                                last_name,
                                emails,
                                phones,
                                active,
                                deleted,
                                deleted_at
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING *
                        ''',
                        (lead.campaign, lead.linkedin_public_identifier, lead.chat_id,
                         lead.first_name, lead.last_name,
                         lead.emails, lead.phones,
                         lead.active, lead.deleted, lead.deleted_at)
                    )
                except psycopg2.errors.UniqueViolation:
                    db.rollback()

                    cursor.execute(
                        '''
                            UPDATE PI.Lead
                            SET first_name = %s,
                                last_name = %s,
                                emails = %s,
                                phones = %s,
                                active = %s,
                                deleted = %s,
                                chat_id = %s
                            WHERE campaign = %s AND linkedin_public_identifier = %s AND deleted = FALSE
                            RETURNING *
                        ''',
                        (lead.first_name, lead.last_name,
                         lead.emails, lead.phones,
                         lead.active, lead.deleted, lead.chat_id, lead.campaign, lead.linkedin_public_identifier)
                    )

                data: dict = cursor.fetchone()

                if data is None:
                    raise APIException(message="Database failed to insert and return data.", context=dict(table="Lead", operation="INSERT"))

                return Lead.model_validate(dict(data))
        except psycopg2.DatabaseError as e:
            db.rollback()

            raise

    @classmethod
    def validate_owner(cls, owner: str):
        ClientController.get(email=owner)

    @classmethod
    def get(cls, owner: str, page_size: int, page: int) -> list[Lead]:
        LeadPersistence.validate_owner(owner=owner)

        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                '''
                SELECT l.*
                FROM PI.Lead l
                JOIN PI.Campaign c ON c.id = l.campaign
                WHERE c.owner = %s AND l.deleted = false AND c.deleted = false
                LIMIT %s OFFSET %s
                ''',
                (owner, page_size, page * page_size)
            )

            data: list[dict] = cursor.fetchall()

            if data is None:
                raise APIException(message="Database failed to return data.", context=dict(table="Lead", operation="SELECT"))

            return [ Lead.model_validate(l) for l in data ]

    @classmethod
    def is_a_valid_lead(cls, owner: str, linkedin_public_identifier: str) -> bool:
        LeadPersistence.validate_owner(owner=owner)

        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                '''
                SELECT 1
                FROM PI.Lead l
                JOIN PI.Campaign c ON c.id = l.campaign
                WHERE c.owner = %s AND l.linkedin_public_identifier = %s AND c.deleted = false AND l.deleted = false
                ''',
                (owner, linkedin_public_identifier)
            )

            return cursor.fetchone() is not None

    @classmethod
    def get_by_owner_and_linkedin_public_identifier(cls, owner: str, linkedin_public_identifier: str) -> Lead:
        LeadPersistence.validate_owner(owner=owner)

        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                '''
                SELECT l.*
                FROM PI.Lead l
                JOIN PI.Campaign c ON c.id = l.campaign
                WHERE c.owner = %s AND l.linkedin_public_identifier = %s AND c.deleted = false AND l.deleted = false
                ''',
                (owner, linkedin_public_identifier)
            )

            data: dict | None = cursor.fetchone()

            if data is None:
                raise InexistentObjectException(message=f"No lead with owner and linkedin_public_identifier: '{(owner, linkedin_public_identifier)}'.")

            return Lead.model_validate(dict(data))

    @classmethod
    def get_by_id(cls, owner: str, id: int) -> Lead:
        LeadPersistence.validate_owner(owner=owner)

        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                '''
                SELECT l.*
                FROM PI.Lead l
                JOIN PI.Campaign c ON c.id = l.campaign
                WHERE c.owner = %s AND l.id = %s AND c.deleted = false AND l.deleted = false
                ''',
                (owner, id)
            )

            data: dict | None = cursor.fetchone()

            if data is None:
                raise InexistentObjectException(message=f"No lead with owner and id: '{(owner, id)}'.")

            return Lead.model_validate(dict(data))
