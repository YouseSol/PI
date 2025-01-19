import uuid

import pydantic

import psycopg2, psycopg2.extras, psycopg2.extensions
import redis

from api.APIConfig import APIConfig


psycopg2.extensions.register_adapter(pydantic.UUID4, lambda obj: psycopg2.extensions.adapt(str(obj)))
psycopg2.extensions.register_adapter(uuid.UUID, lambda obj: psycopg2.extensions.adapt(str(obj)))

global G

G = dict()

def get_postgres_db():
    global G

    POSTGRES_CONFIG = APIConfig.get("Postgres")

    db = G.get("POSTGRES_DATABASE", None)

    if db is None:
        db = G["POSTGRES_DATABASE"] = psycopg2.connect(
            user=POSTGRES_CONFIG["User"],
            password=POSTGRES_CONFIG["Password"],
            host=POSTGRES_CONFIG["Host"],
            port=POSTGRES_CONFIG["Port"],
            dbname=POSTGRES_CONFIG["Database"],
            cursor_factory=psycopg2.extras.RealDictCursor
        )

    return db

def get_redis_db():
    global G

    REDIS_CONFIG = APIConfig.get("Redis")

    db = G.get("REDIS_DATABASE", None)

    if db is None:
        db = G["REDIS_DATABASE"] = redis.Redis(
            host=REDIS_CONFIG["Host"],
            port=REDIS_CONFIG["Port"],
            password=REDIS_CONFIG["Password"],
            decode_responses=REDIS_CONFIG["DecodeResponses"]
        )

    return db
