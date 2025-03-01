import datetime as dt, logging, logging.config, os, traceback

import fastapi

from appconfig import AppConfig

from api.controller.Controller import Controller

from api.route import dependencies

from api.route import auth

from api.route import user
from api.route import linkedin
from api.route import campaign
from api.route import lead
from api.route import sales_representative

from api.route.webhook import linkedin as linkedin_wh


os.environ["OPENAI_API_KEY"] = AppConfig["OpenAI"]["ApiKey"]

logging.config.dictConfig(AppConfig["Logging"])

logger = logging.getLogger(__name__)

api = fastapi.FastAPI(title=AppConfig["Name"],
                      root_path="/api",
                      version="0.1.1")

# # INFO: Necessary only for when developing UI.
# import fastapi.middleware.cors
#
# api.add_middleware(
#     fastapi.middleware.cors.CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
#     allow_credentials=True,
# )

@api.exception_handler(Exception)
async def exception_handler(request: fastapi.Request, exc: Exception):
    Controller.rollback()

    # INFO: This could go to a task queue.
    if os.environ.get("DEV_MODE") == "False":
        moment = dt.datetime.now()

        logger.fatal(
            "Unexpected exception occurred.",
            extra=dict(
                subject=f"{moment.strftime('[%d/%m/%Y %H:%M]')} Unexpected exception occurred in application: {AppConfig['Name']}",
                body=f"An unhandle exception occurred at {moment.strftime('%d/%m/%Y %H:%M:%s')}\n{traceback.format_exc()}",
            )
        )

    return fastapi.responses.JSONResponse(status_code=500, content=dict(message=f"Something went wrong."))

@api.get("/ping")
def ping() -> dict:
    return dict(message="pong")

api.include_router(auth.router)

api.include_router(user.router, dependencies=[ fastapi.Depends(dependencies.has_valid_api_token) ])
api.include_router(sales_representative.router, dependencies=[ fastapi.Depends(dependencies.has_valid_api_token) ])
api.include_router(campaign.router, dependencies=[ fastapi.Depends(dependencies.has_valid_api_token) ])
api.include_router(lead.router, dependencies=[ fastapi.Depends(dependencies.has_valid_api_token) ])

api.include_router(linkedin.router)
api.include_router(linkedin_wh.router)
