from api.persistence.Persistence import Persistence


class Controller(object):

    @classmethod
    def save(cls):
        Persistence.save()

    @classmethod
    def rollback(cls):
        Persistence.rollback()
