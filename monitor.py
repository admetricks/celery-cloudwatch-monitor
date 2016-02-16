from boto.ec2.cloudwatch import CloudWatchConnection
from datetime import datetime
from main import AWS_CREDENTIALS, CLOUDWATCH_NAMESPACE, HOSTNAME_DIMENSIONS

# https://gist.github.com/zircote/7834009


def monitor(app):
    cloudwatch = CloudWatchConnection(**AWS_CREDENTIALS)
    state = app.events.State()

    def get_task(event):
        """
        :rtype: celery.events.state.Task
        """
        state.event(event)
        # task name is sent only with -received event, and state
        # will keep track of this for us.
        return state.tasks.get(event['uuid'])

    def on_task_succeeded(event):
        print('on_task_succeeded', event)
        task = get_task(event)
        if task.name is None:
            return
        dimensions = []
        if HOSTNAME_DIMENSIONS:
            dimensions.append({
                'hostname': task.hostname,
                'task': task.name,
            })
        dimensions.append({
            'task': task.name,
        })
        dtime = datetime.fromtimestamp(task.runtime)
        for dimensions_metric in dimensions:
            cloudwatch.put_metric_data(
                CLOUDWATCH_NAMESPACE, task.type,
                (dtime.second * 1000) + (dtime.microsecond / 1000),
                datetime.fromtimestamp(task.timestamp),
                'Milliseconds', dimensions_metric)

    def on_task_received(event):
        print('on_task_received', event)
        task = get_task(event)
        if task.name is None:
            return
        dimensions = []
        if HOSTNAME_DIMENSIONS:
            dimensions.append({
                'hostname': task.hostname,
                'task': task.name,
            })
        dimensions.append({
            'task': task.name,
        })
        for dimensions_metric in dimensions:
            cloudwatch.put_metric_data(
                CLOUDWATCH_NAMESPACE, task.type, 1,
                datetime.fromtimestamp(task.timestamp),
                'Count', dimensions_metric)

    def on_task_started(event):
        print('on_task_started', event)
        task = get_task(event)
        if task.name is None:
            return
        dimensions = []
        if HOSTNAME_DIMENSIONS:
            dimensions.append({
                'hostname': task.hostname,
                'task': task.name,
            })
        dimensions.append({
            'task': task.name,
        })
        for dimensions_metric in dimensions:
            cloudwatch.put_metric_data(
                CLOUDWATCH_NAMESPACE, task.type, 1,
                datetime.fromtimestamp(task.timestamp),
                'Count', dimensions_metric)

    def on_task_failed(event):
        print('on_task_failed', event)
        task = get_task(event)
        if task.name is None:
            return
        dimensions = []
        if HOSTNAME_DIMENSIONS:
            dimensions.append({
                'hostname': task.hostname,
                'task': task.name,
            })
        dimensions.append({
            'task': task.name,
        })
        for dimensions_metric in dimensions:
            cloudwatch.put_metric_data(
                CLOUDWATCH_NAMESPACE, task.type, 1,
                datetime.fromtimestamp(task.timestamp),
                'Count', dimensions_metric)

    with app.connection() as connection:
        recv = app.events.Receiver(connection, handlers={
            'task-succeeded': on_task_succeeded,
            'task-received': on_task_received,
            'task-started': on_task_started,
            'task-failed': on_task_failed
            # '*': on_task_succeeded,
        })
        recv.capture(limit=None, timeout=None, wakeup=True)

if __name__ == '__main__':
    from main import app
    monitor(app)
