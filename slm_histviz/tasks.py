from celery import Celery, group
from celery.utils.log import get_task_logger

from slm_histviz import app


# =====================================================================================================================
# === general celery app configuration
# =====================================================================================================================

def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379',
    # because apparently everything else is insecure :|
    CELERY_ACCEPT_CONTENT=['json'],
    CELERY_TASK_SERIALIZER='json',
    CELERY_RESULT_SERIALIZER='json',
)
celery = make_celery(app)


# =====================================================================================================================
# === task definitions
# =====================================================================================================================

logger = get_task_logger(__name__)


@celery.task()
def ping():
    print "ping() called, sending pong..."
    return "pong!"
