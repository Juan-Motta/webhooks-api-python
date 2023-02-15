import os
from dotenv import load_dotenv

load_dotenv()

# Config
CONFIG = {
    "secret_key": os.getenv("SECRET_KEY"),
    "debug": os.getenv("DEBUG"),
    "enviroment": os.getenv("ENVIROMENT"),
}

# Database webhooks
WEBHOOKS_DB = {
    "host": os.getenv("DB_WEBHOOKS_HOST"),
    "name": os.getenv("DB_WEBHOOKS_NAME"),
    "user": os.getenv("DB_WEBHOOKS_USER"),
    "password": os.getenv("DB_WEBHOOKS_PASSWORD"),
    "port": os.getenv("DB_WEBHOOKS_PORT"),
}

# Database services
SERVICES_DB = {
    "host": os.getenv("DB_SERVICES_HOST"),
    "name": os.getenv("DB_SERVICES_NAME"),
    "user": os.getenv("DB_SERVICES_USER"),
    "password": os.getenv("DB_SERVICES_PASSWORD"),
    "port": os.getenv("DB_SERVICES_PORT"),
}

# Rabbit
RABBIT = {
    "host": os.getenv("RABBIT_HOST"),
    "user": os.getenv("RABBIT_USER"),
    "password": os.getenv("RABBIT_PASSWORD"),
    "port": int(os.getenv("RABBIT_PORT")),
    "notification_queue": os.getenv("RABBIT_NOTIFICATION_QUEUE"),
    "reconnection_time": os.getenv("RABBIT_RECONNECTION_TIME")
}

# Discord
DISCORD = {
    "url": os.getenv("DISCORD_URL"),
    "notification": os.getenv("NOTIFICATION"),
}
