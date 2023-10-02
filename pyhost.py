# PYHOST
# Pyhost is a completely free and opensource project built by FriendlyFox.exe AKA https://github.com/Ames-Hub
# It is a lightweight, simple replacement for Nginx. It is built in Python and is very easy to use.
# It is mainly built for compatibility with pufferpanel, but it can be used bloody anywhere as its just a python script
# Have fun!
print("Welcome to Pyhost! - A lightweight, simple replacement for Nginx.")
print("https://github.com/Ames-Hub/pyhost")

# Importing modules
import requests, os, logging, datetime
import keyboard # Import keyboard for listening for input, not explicitly doing so with input() as it is blocking and can only be used once
from library.jmod import jmod
from library.application import application
from library.instance import instance

# Ensures all neccesary directories exist
os.makedirs("instances", exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs("data/logs", exist_ok=True)

filename = str(datetime.datetime.now()).replace(':', '.')
# Sets up logging
logging.basicConfig(
    # Gets a readable datetime format for the log filename
    filename=f"data/logs/{filename}.log",
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.basicConfig(
    # Gets a readable datetime format for the log filename
    filename=f"data/logs/{filename}.log",
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)

logging.info("Pyhost logging started successfully!")

# Autostarts the autostarts
# Finds how many autostarts there are
launch_amount = 0
for config_file in os.listdir("instances/"):
    if config_file.endswith(".json"):
        # Gets if the project should autostart
        isTrue = jmod.getvalue(key="autostart", json_dir=f"instances/{config_file}")
        if isTrue is True:
            launch_amount += 1
            print(f"Initializing project: \"{jmod.getvalue(key='name', json_dir=f'instances/{config_file}')}\"")

if launch_amount != 0:
    print(f"AutoLaunching {launch_amount} instances...")
    raise NotImplementedError("AutoLaunch is not yet implemented!")


# The main loop to keep the program running
application.run(
    keybind_listen=bool(os.environ.get("PYHOST_KEYBIND_LISTEN", True))
    )