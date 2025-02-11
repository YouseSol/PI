import logging

import pydantic

from api.domain.Client import LoginForm, RegisterForm, SystemClient

from api.persistence.ClientPersistence import ClientPersistence


logger = logging.getLogger(__name__)

class ClientController(object):

    @classmethod
    def register(cls, form: RegisterForm) -> SystemClient:
        return ClientPersistence.register(form=form)

    @classmethod
    def login(cls, form: LoginForm) -> SystemClient | None:
        return ClientPersistence.login(form=form)

    @classmethod
    def is_api_token_valid(cls, api_token: pydantic.UUID4) -> bool:
        return ClientPersistence.is_api_token_valid(api_token=api_token)

    @classmethod
    def get(cls, email: str) -> SystemClient:
        return ClientPersistence.get(email=email)

    @classmethod
    def get_by_linkedin_account_id(cls, linkedin_account_id: str) -> SystemClient:
        return ClientPersistence.get_by_linkedin_account_id(linkedin_account_id=linkedin_account_id)

    @classmethod
    def get_by_api_token(cls, api_token: pydantic.UUID4) -> SystemClient:
        return ClientPersistence.get_by_api_token(api_token=api_token)

    @classmethod
    def set_active(cls, api_token: pydantic.UUID4, active: bool):
        ClientPersistence.set_active(api_token=api_token, active=active)
