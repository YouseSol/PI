import logging

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from api.domain.Client import Client, SystemClient

from api.controller.SalesRepresentativeController import SalesRepresentativeController

from api.APIConfig import APIConfig
from api.exception.InexistentObjectException import InexistentObjectException


logger = logging.getLogger(__name__)

class ContactController(object):

    @classmethod
    def send_email_to_client(cls, subject: str, message: str, client: SystemClient):
        to = client.email

        try:
            sales_representative = SalesRepresentativeController.get(owner=client.email)
            to = sales_representative.email
        except InexistentObjectException:
            pass

        ContactController.send_email_impl(subject=subject, body=message, to=to)

    @classmethod
    def send_email_to_support(cls, subject: str, message: str):
        for to in APIConfig.get("Support")['Contact']['Responsibles']:
            ContactController.send_email_impl(subject=subject, body=message, to=to)

    @classmethod
    def send_email_impl(cls, subject: str, body: str, to: str):
        from_email = APIConfig.get("Support")['Contact']['Sender']['User']
        from_password = APIConfig.get("Support")['Contact']['Sender']['Password']

        message = MIMEMultipart()
        message['From'] = from_email
        message['To'] = to
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(from_email, from_password)
            server.sendmail(from_email, to, message.as_string())

        logger.info(f"Email sent successfully to: {to}")
