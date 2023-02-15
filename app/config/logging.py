import os

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
        'json': {
            'format': '{"loggerName":"%(name)s", '
                      '"timestamp":"%(asctime)s", '
                      '"fileName":"%(filename)s", '
                      '"logRecordCreationTime":"%(created)f", '
                      '"functionName":"%(funcName)s", '
                      '"levelNo":"%(levelno)s", '
                      '"lineNo":"%(lineno)d", '
                      '"time":"%(msecs)d", "'
                      'levelName":"%(levelname)s", '
                      '"message":"%(message)s", '
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'verbose',
        },
        'log_file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': '/home/app/logs/python-meetups.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 31,
            'formatter': 'json',
        },
    },
    'loggers': {
        'fastapi': {
            'handlers': ['console', 'log_file'],
            'level': os.getenv('FASTAPI_LOG_LEVEL', 'INFO'),
        },
    }
}
