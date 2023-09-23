from dotenv import load_dotenv
from logging.config import dictConfig
import logging
import pathlib
import os

load_dotenv()

#Secrets
DISCORD_API_SECRET =  os.getenv("DISCORD_API_TOKEN")

SAPO_ID =  int(os.getenv("SAPO_ID"))

MONKEY_ID =  int(os.getenv("MONKEY_ID"))

allowed_users = [SAPO_ID, MONKEY_ID]



#For loading cogs
BASE_DIR = pathlib.Path(__file__).parent
COGS_DIR = BASE_DIR / "cogs"



LOGGING_CONFIG = {
    "version":1,
    "disabled_existing_loggers":False,
    "formatters":{
        "verbose":{
            "format": "%(levelname)-10s - %(asctime)s - %(module)-15s : %(message)s"
        },
        "standard":{
            "format": "%(levelname)-10s - %(module)-15s : %(message)s"
        }
    },
    "handlers":{
        "console":{
            'level':"DEBUG",
            'class':"logging.StreamHandler",
            'formatter':"standard"
        },
        "console2":{
            'level':"WARNING",
            'class':"logging.StreamHandler",
            'formatter':"standard"
        },
        "file":{
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "logs/infos.log",
            "mode": "w",
            "formatter": "verbose"
        }

    },
    "loggers":{
        "bot":{
            'handlers':['console',"file"],
            "level":"INFO",
            "propagate":False
        },
        "discord":{
            'handlers':['console2',"file"],
            "level": "INFO",
            "propagate": False
        }
    }

}
dictConfig(LOGGING_CONFIG)