# Broker settings
BROKER_URL = 'sqla+sqlite:///celery.db'
CELERY_RESULT_DBURI = "sqlite:///celery.db"

# List of modules to import when celery starts.
CELERY_IMPORTS = ("app.tasks",)

# Using the database to store task state and results.
CELERY_RESULT_BACKEND = "database"
CELERY_RESULT_DBURI = "sqlite:///celery.db"

# Logging
CELERYD_LOG_DEBUG='FALSE'
CELERYD_LOG_LEVEL='ERROR'
CELERYD_LOG_FILE='celery.log'
