import json, logging, time

import smtplib
import email.mime.multipart
import email.mime.text

import requests
import celery

from taskmanager.APIConfig import APIConfig

from taskmanager.connector import get_redis_db


app = celery.Celery(__name__)

app.conf.update(broker_url=APIConfig.get("Celery")["BrokerURL"],
                result_backend=APIConfig.get("Celery")["ResultBackend"])

logger = logging.getLogger(__name__)

@app.task(name="trigger-chat-answer")
def trigger_chat_answer():
    start_time = time.time()

    task_cfg = APIConfig().get("Tasks")["TriggerChatAnswer"]

    db = get_redis_db()

    session = requests.session()

    keys: list[str] = db.keys("TASK_TRIGGER_CHAT_ANSWER-*")

    for task_key in keys:
        if time.time() - start_time > task_cfg["MaxExecutionTime"]:
            logger.warning("Stopping execution: max time reached")
            break

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

    session.close()

@app.task(name="send-email")
def send_email(to: str, subject: str, body: str):
    from_email = APIConfig.get("Support")['Contact']['Sender']['User']
    from_password = APIConfig.get("Support")['Contact']['Sender']['Password']

    message = email.mime.multipart.MIMEMultipart()
    message['From'] = from_email
    message['To'] = to
    message['Subject'] = subject
    message.attach(email.mime.text.MIMEText(body, 'plain'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(from_email, from_password)
        server.sendmail(from_email, to, message.as_string())

    logger.info(f"Email sent successfully to: {to}")
