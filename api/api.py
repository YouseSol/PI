import datetime as dt

import logging
import logging.config

import traceback

import os

import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import fastapi

from api.APIConfig import APIConfig

from api.controller.Controller import Controller

from api.route import dependencies

from api.route import auth
from api.route import user
from api.route import linkedin
from api.route import alessia
from api.route import lead

from api.route.webhook import linkedin as linkedin_wh


logging.config.dictConfig(APIConfig.get("Logging"))

logger = logging.getLogger(__name__)

api = fastapi.FastAPI(title=APIConfig.get("Name"),
                      root_path="/api",
                      version="0.1.1")

def sent_email(subject: str, body: str, to: str):
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

@api.exception_handler(Exception)
async def exception_handler(request: fastapi.Request, exc: Exception):
    Controller.rollback()

    logger.fatal("Unexpected exception occurred:\n", exc_info=True)

    # INFO: This could go to a task queue.
    if os.environ.get("DEV_MODE") == "False":
        try:
            moment = dt.datetime.now()

            for email in APIConfig.get("Support")['Contact']['Responsibles']:
                sent_email(
                    subject=f"{moment.strftime('[%d/%m/%Y %H:%M]')} Unexpected exception occurred in application: {APIConfig.get('Name')}",
                    body=f"An unhandle exception occurred at {moment.strftime('%d/%m/%Y %H:%M:%s')}\n{traceback.format_exc()}",
                    to=email
                )
        except:
            logger.fatal(f"Failed to sent warning email.", exc_info=True)

    return fastapi.responses.JSONResponse(status_code=500, content=dict(message=f"Something went wrong."))

@api.get("/ping")
def ping() -> dict:
    return dict(message="pong")

api.include_router(auth.router)

api.include_router(user.router, dependencies=[ fastapi.Depends(dependencies.has_valid_api_token) ])
api.include_router(lead.router, dependencies=[ fastapi.Depends(dependencies.has_valid_api_token) ])
api.include_router(alessia.router, dependencies=[ fastapi.Depends(dependencies.has_valid_api_token) ])
api.include_router(linkedin.router)

api.include_router(linkedin.router)
api.include_router(linkedin_wh.router)
