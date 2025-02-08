import json, logging, time

import requests

import celery

from taskmanager.APIConfig import APIConfig

from taskmanager.connector import get_redis_db

import celery


app = celery.Celery(__name__)

app.conf.update(broker_url=APIConfig.get("Celery")["BrokerURL"],
                result_backend=APIConfig.get("Celery")["ResultBackend"])

logger = logging.getLogger(__name__)

@app.task(name="trigger-chat-answer")
def trigger_chat_answer():
    task_cfg = APIConfig().get("Tasks")["TriggerChatAnswer"]

    db = get_redis_db()

    session = requests.session()

    keys: list[str] = db.keys("TASK_TRIGGER_CHAT_ANSWER-*")

    for task_key in keys:
        time.sleep(30)

        task = json.loads(db.get(task_key))

        client: dict = task["client"]
        lead: dict = task["lead"]
        timestamp: float = task.pop("timestamp")

        if time.time() - timestamp < task_cfg["InQueueLifeTime"]:
            continue

        response = session.post(task_cfg["GenerateResponseURI"], data=json.dumps(task))

        if response.ok:
            db.delete(task_key)
        else:
            logger.fatal(f"Failed to trigger chat answer: {response.status_code, response.reason}")
