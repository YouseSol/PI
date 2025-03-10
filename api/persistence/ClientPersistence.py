import datetime as dt, logging

import psycopg2, pydantic

from werkzeug.security import generate_password_hash, check_password_hash

from api.domain.Client import LoginForm, RegisterForm, SystemClient

from api.persistence.connector import get_postgres_db

from api.exception.APIException import APIException
from api.exception.DuplicatingObjectException import DuplicatingObjectException
from api.exception.InexistentObjectException import InexistentObjectException


logger = logging.getLogger(__name__)

class ClientPersistence(object):

    @classmethod
    def register(cls, form: RegisterForm) -> SystemClient:
        db = get_postgres_db()

        try:
            with db.cursor() as cursor:
                cursor.execute(
                    '''
                        INSERT INTO PI.Client(
                            email,
                            first_name,
                            last_name,
                            standard_message,
                            linkedin_account_id,
                            hash,
                            created_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING *;
                    ''',
                    (form.email,
                     form.first_name, form.last_name,
                     form.standard_message, form.linkedin_account_id, generate_password_hash(form.password),
                     dt.datetime.now())
                )

                data: dict = cursor.fetchone()

                if data is None:
                    raise APIException(message="Database failed to insert and return data.", context=dict(table="Client", operation="INSERT"))

                return SystemClient.model_validate(dict(data))
        except psycopg2.DatabaseError as e:
            db.rollback()

            if isinstance(e, psycopg2.errors.UniqueViolation):
                raise DuplicatingObjectException(f"Already exists an account with email: '{form.email}'.")
            else:
                raise

    @classmethod
    def update_password(cls, client: SystemClient, password: str) -> SystemClient:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                "UPDATE PI.Client SET hash = %s WHERE email = %s AND deleted = false RETURNING *",
                (generate_password_hash(password), client.email)
            )

            data: dict = cursor.fetchone()

            if data is None:
                raise APIException(message="Database failed to insert and return data.", context=dict(table="Client", operation="UPDATE"))

            return SystemClient.model_validate(dict(data))

    @classmethod
    def login(cls, form: LoginForm) -> SystemClient | None:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM PI.Client WHERE email = %s AND deleted = false",
                (form.email, )
            )

            data: dict = cursor.fetchone()

            if data is not None and check_password_hash(data['hash'], form.password):
                return SystemClient.model_validate(dict(data))

    @classmethod
    def set_active(cls, client: SystemClient, active: bool) -> None:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                "UPDATE PI.Client SET active = %s WHERE token = %s AND deleted = false",
                (active, client.token)
            )

    @classmethod
    def is_api_token_valid(cls, api_token: pydantic.UUID4) -> bool:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) as count FROM PI.Client WHERE token = %s AND deleted = false",
                (api_token, )
            )

            data: dict = cursor.fetchone()

            if data is None:
                raise APIException(message="Database failed to return data.", context=dict(table="Client", operation="SELECT"))

            return data["count"] == 1

    @classmethod
    def get_by_email(cls, email: str) -> SystemClient:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM PI.Client WHERE email = %s AND deleted = false",
                (email, )
            )

            data: dict = cursor.fetchone()

            if data is None:
                raise InexistentObjectException(message=f"No client with email: '{email}'.")

            return SystemClient.model_validate(dict(data))

    @classmethod
    def get_by_linkedin_account_id(cls, linkedin_account_id: str) -> SystemClient:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM PI.Client WHERE linkedin_account_id = %s AND deleted = false",
                (linkedin_account_id, )
            )

            data: dict = cursor.fetchone()

            if data is None:
                raise InexistentObjectException(message=f"No client with linkedin_account_id: '{linkedin_account_id}'.")

            return SystemClient.model_validate(dict(data))

    @classmethod
    def get_by_api_token(cls, api_token: pydantic.UUID4) -> SystemClient:
        db = get_postgres_db()

        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM PI.Client WHERE token = %s AND deleted = false",
                (api_token, )
            )

            data: dict = cursor.fetchone()

            if data is None:
                raise InexistentObjectException(message=f"No client with token: '{api_token}'.")

            return SystemClient.model_validate(dict(data))
