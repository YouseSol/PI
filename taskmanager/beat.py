import celery

from taskmanager.APIConfig import APIConfig

from taskmanager.worker import trigger_chat_answer, send_email


app = celery.Celery(__name__)

app.conf.update(broker_url=APIConfig.get("Celery")["BrokerURL"],
                result_backend=APIConfig.get("Celery")["ResultBackend"])

if app.on_after_configure is None:
    exit(0)

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        APIConfig.get("Tasks")["TriggerChatAnswer"]["FrequencyInSeconds"],
        trigger_chat_answer.s(),
        name="Trigger chat answer."
    )
