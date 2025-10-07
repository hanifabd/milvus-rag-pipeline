
from UtilityInsertInformation import InsertInformation
from celery import Celery

insert_app = Celery(
    'insert_information',
    broker='amqp://guest:guest@localhost:5672',  # RabbitMQ as broker
    backend='db+sqlite:///task_status.sqlite'    # SQLite as result backend
)

@insert_app.task(bind=True)
def insert_information_worker(self, data):
    self.update_state(state="PROGRESS")
    insert_engine = InsertInformation()
    result = insert_engine.insert_information(**data)
    return result