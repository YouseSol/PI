import logging

import psycopg2

from api.persistence.connector import get_postgres_db

from api.domain.Client import SystemClient
from api.domain.Campaign import SystemCampaign
from api.domain.Lead import SystemLead

from api.exception.APIException import APIException
from api.exception.InexistentObjectException import InexistentObjectException


logger = logging.getLogger(__name__)

class LeadPersistence(object):

    @classmethod
    def save(cls, lead: SystemLead) -> SystemLead:
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
                                feedback,
                                active,
                                deleted,
                                deleted_at
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING *
                        ''',
                        (lead.campaign, lead.linkedin_public_identifier, lead.chat_id,
                         lead.first_name, lead.last_name,
                         lead.emails, lead.phones,
                         lead.feedback,
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
                                feedback = %s,
                                active = %s,
                                deleted = %s,
                                chat_id = %s
                            WHERE campaign = %s AND linkedin_public_identifier = %s AND deleted = FALSE
                            RETURNING *
                        ''',
                        (lead.first_name, lead.last_name,
                         lead.emails, lead.phones,
                         lead.feedback,
                         lead.active, lead.deleted, lead.chat_id, lead.campaign, lead.linkedin_public_identifier)
                    )

                data: dict = cursor.fetchone()

                if data is None:
                    raise APIException(message="Database failed to insert and return data.", context=dict(table="Lead", operation="INSERT"))

                return SystemLead.model_validate(dict(data))
        except psycopg2.DatabaseError as e:
            db.rollback()

            raise

    @classmethod
    def is_a_valid_lead(cls, client: SystemClient, linkedin_public_identifier: str) -> bool:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                '''
                SELECT 1
                FROM PI.Lead l
                JOIN PI.Campaign c ON c.id = l.campaign
                WHERE c.owner = %s AND l.linkedin_public_identifier = %s AND c.deleted = false AND l.deleted = false
                ''',
                (client.email, linkedin_public_identifier)
            )

            return cursor.fetchone() is not None

    @classmethod
    def get_by_linkedin_public_identifier(cls, client: SystemClient, linkedin_public_identifier: str) -> SystemLead:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                '''
                SELECT l.*
                FROM PI.Lead l
                JOIN PI.Campaign c ON c.id = l.campaign
                WHERE c.owner = %s AND l.linkedin_public_identifier = %s AND c.deleted = false AND l.deleted = false
                ''',
                (client.email, linkedin_public_identifier)
            )

            data: dict | None = cursor.fetchone()

            if data is None:
                raise InexistentObjectException(message=f"No lead with owner and linkedin_public_identifier: '{(client.email, linkedin_public_identifier)}'.")

            return SystemLead.model_validate(dict(data))

    @classmethod
    def get_by_id(cls, client: SystemClient, id: int) -> SystemLead:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                '''
                SELECT l.*
                FROM PI.Lead l
                JOIN PI.Campaign c ON c.id = l.campaign
                WHERE c.owner = %s AND l.id = %s AND c.deleted = false AND l.deleted = false
                ''',
                (client.email, id)
            )

            data: dict | None = cursor.fetchone()

            if data is None:
                raise InexistentObjectException(message=f"No lead with owner and id: '{(client.email, id)}'.")

            return SystemLead.model_validate(dict(data))

    @classmethod
    def count_client_leads(cls, client: SystemClient) -> int:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                '''
                SELECT COUNT(*) AS count
                FROM PI.Lead l
                JOIN PI.Campaign c ON c.id = l.campaign
                WHERE c.owner = %s AND l.deleted = false AND c.deleted = false
                ''',
                (client.email, )
            )

            data: dict = cursor.fetchone()

            if data is None:
                raise APIException(message="Database failed to return data.", context=dict(table="Lead", operation="SELECT"))

            return data["count"]

    @classmethod
    def paginate_client_leads(cls, client: SystemClient, page_size: int, page: int) -> list[SystemLead]:
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
                (client.email, page_size, page * page_size)
            )

            data: list[dict] = cursor.fetchall()

            if data is None:
                raise APIException(message="Database failed to return data.", context=dict(table="Lead", operation="SELECT"))

            return [ SystemLead.model_validate(l) for l in data ]

    @classmethod
    def count_leads_in_campaign(cls, campaign: SystemCampaign) -> int:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) as count FROM PI.Lead WHERE campaign = %s AND deleted = false",
                (campaign.id, )
            )

            data: dict = cursor.fetchone()

            if data is None:
                raise APIException(message="Database failed to return data.", context=dict(table="Campaign", operation="SELECT"))

            return data["count"]

    @classmethod
    def paginate_leads_in_campaign(cls,
                                   campaign: SystemCampaign,
                                   query: str,
                                   is_active: bool | None, has_conversation: bool | None,
                                   page: int, page_size: int) -> list[SystemLead]:
        db = get_postgres_db()

        q = f'%{query}%'

        with db.cursor() as cursor:
            cursor.execute(
                '''
                SELECT l.*
                FROM PI.Lead l JOIN PI.Campaign c ON c.id = %(cid)s
                WHERE l.deleted = false
                  AND (l.first_name ILIKE %(query)s OR l.last_name ILIKE %(query)s)
                  AND (
                    %(filter_by_is_active_flag)s
                    OR
                    l.active = %(is_active)s
                  )
                  AND (
                    %(filter_by_has_conversation_flag)s
                    OR
                    (%(has_conversation)s AND l.chat_id IS NOT NULL)
                    OR
                    (NOT %(has_conversation)s AND l.chat_id IS NULL)
                  )
                ORDER BY l.id
                LIMIT %(page_size)s OFFSET %(offset)s
                ''',
                dict(cid=campaign.id,
                     query=q,
                     filter_by_is_active_flag=is_active is None, is_active=is_active,
                     filter_by_has_conversation_flag=has_conversation is None, has_conversation=has_conversation,
                     page_size=page_size, offset=page * page_size)
            )

            data: list[dict] = cursor.fetchall()

            if data is None:
                raise APIException(message="Database failed to return data.", context=dict(table="Lead", operation="SELECT"))

            return [ SystemLead.model_validate(l) for l in data ]
