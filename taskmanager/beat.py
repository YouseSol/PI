import celery

from appconfig import AppConfig

from taskmanager.worker import trigger_chat_answer



app = celery.Celery(__name__)

app.conf.update(broker_url=AppConfig["Celery"]["BrokerURL"],
                result_backend=AppConfig["Celery"]["ResultBackend"])

if app.on_after_configure is None:
    exit(0)

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        AppConfig["Tasks"]["TriggerChatAnswer"]["FrequencyInSeconds"],
        trigger_chat_answer.s(),
        name="Trigger chat answer."
    )
