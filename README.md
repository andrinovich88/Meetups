![logo.jpg](images/logo.jpg)
# python-meetup

## How to install

1. Clone github repo
```bash
gh repo clone modsen-software/python-meetup
```

2. Rename "example.env" to ".env". To use an external 'datadog' logging system, 
   enter the value of your api-key for the 'DD_API_KEY' variable

3. To run the project, use the following command:
```bash
docker-compose up
```

## Features
1. Creation of reports in csv and pdf formats
2. Search for upcoming meetups by geolocation
3. The application partially uses websockets
4. New user email authentication
5. External logging system "datadog" is used


## List of endpoints
![endpoints.png](images/endpoints.png)

### Service endpoints
1. http://127.0.0.1:8000/docs - swagger autodoc system
2. http://127.0.0.1:15672/ - RabbitMQ monitoring system (user - guest, pass - guest)
3. http://127.0.0.1:8001/ - Celery flower monitoring system
4. http://127.0.0.1:5601/kibana/app/home#/ - ElasticSearch monitoring system provided by kibana

## Environment variables

|                  Name                  |                       Description                        |              Ex. value               |
|:--------------------------------------:|:--------------------------------------------------------:|:------------------------------------:|
|                `DEBUG`                 |               `Status of the application`                |                 `1`                  |
|              `SECRET_KEY`              |             `Secret key of the application`              |     `12asd%12bihn256!@@451safb`      |
|                 `ENV`                  |            `Current application environemnt`             |               `local`                |
|        `FASTAPI_SUPERUSER_NAME`        |                     `superuser name`                     |               `admin`                |
|        `FASTAPI_SUPERUSER_PASS`        |                   `superuser password`                   |          `StrongPassword%`           |
|       `FASTAPI_SUPERUSER_EMAIL`        |                    `superuser email`                     |          `admin@gmail.com`           |
|            `MAIL_USERNAME`             |           `email to send verification emails`            |    `pythonmeetups2023@gmail.com`     |
|              `MAIL_ADMIN`              |                      `admin email`                       |          `admin@metups.com`          |
|            `MAIL_PASSWORD`             |  `password to access email to send verification emails`  |          `azjsjiwgredjfjrg`          |
|              `MAIL_PORT`               |       `mail port for sending verification emails`        |                `587`                 |
|             `MAIL_SERVER`              |                  `email server address`                  |           `smtp.gmail.com`           |
|              `MAIL_FROM`               |       `email used in signing verification emails`        |         `admin@meetups.com`          | 
|               `PG_NAME`                |               `Database name for accsess`                |              `fastapi`               |
|               `PG_USER`                |              `Database username for access`              |              `fastapi`               |
|             `PG_PASSWORD`              |              `Database password for access`              |              `fastapi`               |
|               `PG_HOST`                |                `Database host for access`                |              `postgres`              |
|          `POSTGRES_PASSWORD`           |                   `Database password`                    |              `fastapi`               |
|             `POSTGRES_DB`              |                     `Database name`                      |              `fastapi`               |
|            `POSTGRES_USER`             |                   `Database username`                    |              `fastapi`               |
|          `CELERY_BROKER_URL`           |             `message broker url for celery`              | `amqp://guest:guest@rabbitmq:5672//` |
|        `CELERY_RESULT_BACKEND`         |    `backend url for sending task processing results`     |               `rpc://`               |
|                `SCHEMA`                |     `JSON Schema Location of ElasticSearch Indexes`      |       `/home/app/schema.json`        |
|          `ELASTICSEARCH_HOST`          |           `hostname of running ElasticSearch`            |           `elasticsearch`            |
|          `ELASTICSEARCH_PORT`          |             `port of running ElasticSearch`              |                `9200`                |
|              `REDIS_HOST`              |               `hostname of running redis`                |               `redis`                |
|              `REDIS_PORT`              |                 `port of running redis`                  |                `9200`                |
|               `REDIS_DB`               |                    `redis db number`                     |                 `0`                  |
|              `DD_API_KEY`              |       `API key for usage external logging system`        |      `your_api_key_for_datadog`      |
| `DD_LOGS_CONFIG_CONTAINER_COLLECT_ALL` |    `flag to limit the collection of logging messages`    |               `false`                |
|      `DD_CONTAINER_EXCLUDE_LOGS`       | `name of the container excluded from the logging system` |            `name:datadog`            |
|    `DD_DOGSTATSD_NON_LOCAL_TRAFFIC`    |                `AMQP Dead letter qeueue`                 |            `failed_tasks`            |
|               `DD_SITE`                |           `site for sending logging messages`            |            `datadoghq.eu`            |
|           `DD_LOGS_ENABLED`            |     `general switch of the external logging system`      |                `true`                |
  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------