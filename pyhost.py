# PYHOST
# Pyhost is a completely free and opensource project built by FriendlyFox.exe AKA https://github.com/Ames-Hub
# It is a lightweight, simple replacement for Nginx. It is built in Python and is very easy to use.
# It is mainly built for compatibility with pufferpanel, but it can be used bloody anywhere as its just a python script
# Have fun!

# Importing modules
import os, logging, datetime
from library.jmod import jmod
from library.application import application
from library.instance import instance

os.system('cls' if os.name == "nt" else "clear")
print("Welcome to Pyhost! - A lightweight, simple replacement for Nginx.")
print("https://github.com/Ames-Hub/pyhost\n")

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
for app in os.listdir("instances/"):
    config_file = f"instances/{app}/config.json"
    if jmod.getvalue(key=f"{app}.autostart", json_dir=f"{config_file}") == True:
        print(f"Initializing project: \"{jmod.getvalue(key='name', json_dir=f'{config_file}')}\"")
        instance.manage(app, start=True)
        launch_amount += 1

if launch_amount != 0:
    print(f"AutoLaunching {launch_amount} instances...")

# The main loop to keep the program running
application.run(
    keybind_listen=bool(os.environ.get("PYHOST_KEYBIND_LISTEN", True))
    )