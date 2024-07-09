from pathlib import Path
from django.conf import settings
from .models import Settings
import logging.config


def update_globals():
    global SYS_SETTINGS, VARS

    settings_db = {item["name"]: item for item in Settings.objects.all().values()}
    for name, value in settings.SYS_SETTINGS.items():
        if settings_db.get(name):
            settings.SYS_SETTINGS[name] = settings_db[name]["value"]

    VARS = {
        "data_dir": Path(settings.BASE_DIR).joinpath("data"),
        "snmp_get": Path(settings.SYS_SETTINGS["snmp_bin"]).joinpath("snmpget"),
        "snmp_walk": Path(settings.SYS_SETTINGS["snmp_bin"]).joinpath("snmpwalk"),
        "nfdump": Path(settings.SYS_SETTINGS["nfdump_bin"]).joinpath("nfdump"),
    }

    Path(VARS["data_dir"]).mkdir(parents=True, exist_ok=True)

    if "loggers" in settings.LOGGING:
        settings.LOGGING["loggers"]["django"]["level"] = settings.SYS_SETTINGS[
            "logging_level"
        ]

        if settings.SYS_SETTINGS["log_type"] == "file":
            settings.LOGGING["handlers"].update(
                {
                    "file": {
                        "level": settings.SYS_SETTINGS["logging_level"],
                        "class": "logging.FileHandler",
                        "filename": Path(settings.SYS_SETTINGS["log_file"]),
                        "formatter": "simple",
                    },
                }
            )
            settings.LOGGING["loggers"]["django"].update({"handlers": ["file"]})

        logging.config.dictConfig(settings.LOGGING)
    else:
        raise KeyError("'loggers' key not found in LOGGING configuration")


try:
    update_globals()
except Exception as e:
    logging.getLogger("django").critical(f"Error updating globals: {e}")
