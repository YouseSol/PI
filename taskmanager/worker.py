import json, logging, time

import smtplib
import email.mime.multipart
import email.mime.text

import celery, requests

from appconfig import AppConfig

from taskmanager.connector import get_redis_db


app = celery.Celery(__name__)

app.conf.update(broker_url=AppConfig["Celery"]["BrokerURL"],
                result_backend=AppConfig["Celery"]["ResultBackend"])

logger = logging.getLogger(__name__)

@app.task(name="trigger-chat-answer")
def trigger_chat_answer():
    start_time = time.time()

    task_cfg = AppConfig().get("Tasks")["TriggerChatAnswer"]

    db = get_redis_db()

    session = requests.session()

    keys: list[str] = db.keys("TASK_TRIGGER_CHAT_ANSWER-*")

    for task_key in keys:
        if time.time() - start_time > task_cfg["MaxExecutionTime"]:
            logger.debug("Stopping execution: max time reached")
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
            message = f"Failed to answer chat: {response.status_code, response.reason}"

            logger.fatal(message)

            for email_responsible in AppConfig["Support"]["Contact"]["Responsibles"]:
                send_email(to=email_responsible, subject="Failed to anwer chat.", body=message)

    session.close()

@app.task(name="send-email", autoretry_for=(Exception, ), retry_backoff=2)
def send_email(to: str, subject: str, body: str):
    try:
        from_email = AppConfig["Support"]['Contact']['Sender']['User']
        from_password = AppConfig["Support"]['Contact']['Sender']['Password']

        message = email.mime.multipart.MIMEMultipart()
        message['From'] = from_email
        message['To'] = to
        message['Subject'] = subject
        message.attach(email.mime.text.MIMEText(body, 'plain'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(from_email, from_password)
            server.sendmail(from_email, to, message.as_string())

        logger.info(f"Email sent successfully to: {to}")
    except:
        logger.fatal(f"Failed to send email. {json.dumps(dict(to=to, subject=subject, body=body), indent=2, ensure_ascii=False)}")
        raise
