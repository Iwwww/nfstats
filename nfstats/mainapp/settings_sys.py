from .models import Settings
import logging
from logging.handlers import WatchedFileHandler
from pathlib import Path
import django.conf
from django.http import JsonResponse

BASE_DIR = Path(__file__).resolve().parent.parent

ALLOWED_HOSTS = ["nfstats.example.com"]

SYS_SETTINGS = {
    "log_file": "/var/log/nfstats.log",
    "log_type": "console",
    "logging_level": "DEBUG",
    "nfdump_bin": "/usr/bin/",
    "snmp_bin": "/usr/bin",
    "snmp_ver": "2c",
    "history_days": 10,
}

VARS = {}


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s %(levelname)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": [SYS_SETTINGS["log_type"]],
            "level": SYS_SETTINGS["logging_level"],
            "propagate": True,
        },
    },
}

DATABASES = {
    "default": {
        #'ENGINE': 'django.db.backends.mysql',
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "nfstats_db",
        "USER": "nfstats_dbuser",
        "PASSWORD": "nfstatsdbpass",
        "HOST": "localhost",
        "PORT": "5432",
    }
}


# Logging configuration
logger = logging.getLogger("django")
