import logging

import psycopg2

from api.persistence.connector import get_postgres_db

from api.domain.MessageSent import MessageSent


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
                            sent_at
                        )
                        VALUES (%s, %s, %s)
                        RETURNING *
                    ''',
                    (message_sent.id,
                     message_sent.lead,
                     message_sent.sent_at)
                )

                data: dict = cursor.fetchone()

                if data is None:
                    raise APIException(message="Database failed to insert and return data.", context=dict(table="MessageSent", operation="INSERT"))

                return MessageSent.model_validate(dict(data))
        except psycopg2.DatabaseError as e:
            db.rollback()

            raise
