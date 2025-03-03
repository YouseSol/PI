import logging

import psycopg2

from api.domain.Lead import SystemLead
from api.domain.MessageSent import MessageSent

from api.exception.InexistentObjectException import InexistentObjectException
from api.persistence.connector import get_postgres_db


logger = logging.getLogger(__name__)

class MessageSentPersistence(object):

    @classmethod
    def save(cls, message_sent: MessageSent) -> MessageSent:
        db = get_postgres_db()

        try:
            with db.cursor() as cursor:
                cursor.execute(
                    '''
                        INSERT INTO PI.MessageSent(
                            id,
                            lead,
                            sent_at,
                            feedback
                        )
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            lead = EXCLUDED.lead,
                            sent_at = EXCLUDED.sent_at,
                            feedback = EXCLUDED.feedback
                        RETURNING *
                    ''',
                    (message_sent.id,
                     message_sent.lead,
                     message_sent.sent_at,
                     message_sent.feedback)
                )

                data: dict = cursor.fetchone()

                if data is None:
                    raise APIException(message="Database failed to insert and return data.", context=dict(table="MessageSent", operation="INSERT"))

                return MessageSent.model_validate(dict(data))
        except psycopg2.DatabaseError as e:
            db.rollback()

            raise

    @classmethod
    def get_by_message_id(cls, lead: SystemLead, message_id: str) -> MessageSent:
        db = get_postgres_db()

        try:
            with db.cursor() as cursor:
                cursor.execute(
                    '''
                    SELECT m.* FROM PI.MessageSent m
                    WHERE m.lead = %s AND m.id = %s
                    ''',
                    (lead.id, message_id)
                )

                data: dict = cursor.fetchone()

                if data is None:
                    raise InexistentObjectException(message=f"Could not find message id '{message_id}' for lead '{lead.id}'.")

                return MessageSent.model_validate(dict(data))
        except psycopg2.DatabaseError as e:
            db.rollback()

            raise

    @classmethod
    def exist(cls, lead: SystemLead, message_id: str) -> bool:
        db = get_postgres_db()

        try:
            with db.cursor() as cursor:
                cursor.execute(
                    '''
                    SELECT 1 AS exist FROM PI.MessageSent m
                    WHERE m.lead = %s AND m.id = %s
                    ''',
                    (lead.id, message_id)
                )

                data: dict = cursor.fetchone()

                return not data is None
        except psycopg2.DatabaseError as e:
            db.rollback()

            raise
