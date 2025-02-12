import celery

from appconfig import AppConfig

from api.domain.Client import Client, SystemClient

from api.controller.SalesRepresentativeController import SalesRepresentativeController

from api.exception.InexistentObjectException import InexistentObjectException


class ContactController(object):

    @classmethod
    def send_email_to_client(cls, subject: str, body: str, client: SystemClient):
        to = client.email

        try:
            sales_representative = SalesRepresentativeController.get(owner=client.email)
            to = sales_representative.email
        except InexistentObjectException:
            pass

        ContactController.send_email_impl(to=to, subject=subject, body=body)

    @classmethod
    def send_email_to_support(cls, subject: str, body: str):
        for to in AppConfig["Support"]['Contact']['Responsibles']:
            ContactController.send_email_impl(to=to, subject=subject, body=body)

    @classmethod
    def send_email_impl(cls, to: str, subject: str, body: str):
        celery.Celery('celery_invoker', broker=AppConfig["Celery"]["BrokerURL"]) \
              .send_task("send-email", args=[ to, subject, body ])
