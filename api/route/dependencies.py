import typing as t

import fastapi
import pydantic

from api.controller.ClientController import ClientController


async def has_valid_api_token(pi_api_token: t.Annotated[pydantic.UUID4, fastapi.Header()]):
    if not ClientController.is_api_token_valid(api_token=pi_api_token):
        raise fastapi.exceptions.HTTPException(status_code=400, detail="Invalid PI API token.")
