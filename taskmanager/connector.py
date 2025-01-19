import redis

from taskmanager.APIConfig import APIConfig


global G

G = dict()

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
