import os
from celery import Celery

broker_url = os.environ.get('BROKER_URL') or 'amqp://'

AWS_CREDENTIALS = {}
CLOUDWATCH_NAMESPACE = os.environ.get('CLOUDWATCH_NAMESPACE') or 'celery'
app = Celery(broker=broker_url)
