from api.persistence.connector import get_postgres_db


class Persistence(object):

    @classmethod
    def save(cls):
        get_postgres_db().commit()

    @classmethod
    def rollback(cls):
        get_postgres_db().rollback()
