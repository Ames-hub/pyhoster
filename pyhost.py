# PYHOST
# Pyhost is a completely free and opensource project built by FriendlyFox.exe AKA https://github.com/Ames-Hub
# It is a lightweight, simple replacement for Nginx. It is built in Python and is very easy to use.
# It is mainly built for compatibility with pufferpanel, but it can be used bloody anywhere as its just a python script
# Have fun!

# Importing modules
import os, logging, datetime, multiprocessing as threading, shutil
from library.jmod import jmod
from library.application import application
from library.instance import instance
from library.data_tables import config_dt, app_settings

if __name__ == "__main__": # Checks if the user is running the app for the first time
    first_launch = jmod.getvalue("first_launch", "settings.json", True, dt=app_settings)
    if first_launch == True:
        # Checks if the user has backups from a previous pyhost install
        linux = os.name != "nt" # If the OS is linux, it will be true
        if linux:
            backup_dir = f"/var/pyhoster/backups/"
        else:
            # Gets the appdata directory for the user
            appdata = os.getenv("APPDATA")
            backup_dir = f"{appdata}/pyhoster/backups/"

        if os.path.exists(backup_dir) == True:
            found_apps = os.listdir(backup_dir)
            if len(found_apps) != 0:
                print("Found backups from a previous install! Would you like to import them? (y/n)")
                try:
                    answer = input("> ").lower()
                    assert answer == "y" or answer == "n"
                except KeyboardInterrupt:
                    print("Exiting...")
                    exit()
                except AssertionError:
                    print("Invalid choice! Must be 'y' (yes) or 'n' (no)")
                    exit()
                if answer.lower() == "y":
                    print("Importing backups...")
                    for app in found_apps:
                        print(f"Importing {app}...")
                        # All vers inside the "app" folder will be formatted as "ver<version number>". This will get the app with the highest version number
                        versions = os.listdir(f"{backup_dir}/{app}")
                        highest_version = 0
                        for ver in versions:
                            if int(ver.replace("ver", "")) > highest_version:
                                highest_version = int(ver.replace("ver", ""))

                        shutil.copytree(src=f"{backup_dir}/{app}/ver{highest_version}", dst=f"instances/{app}", dirs_exist_ok=True)
                    print("Finished importing backups!")
                else:
                    print("Skipping backup import...")

        # Sets the first_launch setting to false as the user has now launched the app
        jmod.setvalue(
            key="first_launch",
            json_dir="settings.json",
            value=False,
            dt=app_settings
        )

main_pid = os.getpid()
if __name__ == "__main__": # Prevents errors with multiprocessing
    os.system('cls' if os.name == "nt" else "clear")
    print(f"({main_pid}) Welcome to Pyhost! - A lightweight, simple replacement for Nginx.")
    print("https://github.com/Ames-Hub/pyhost\n")
    print("Message from developer:\nHello! If you have any issues, let me know and I will personally help out!\n")

# Ensures all neccesary directories exist
os.makedirs("instances", exist_ok=True)
os.makedirs("logs", exist_ok=True)

log_filename = str(datetime.date.today().strftime("%Y-%m-%d"))
# Sets up logging
logging.basicConfig(
    # Gets a readable datetime format for the log filename
    filename=f"logs/{log_filename}.log",
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.basicConfig(
    # Gets a readable datetime format for the log filename
    filename=f"logs/{log_filename}.log",
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)
logging.info("Pyhost logging started successfully!")

if __name__ == '__main__': # Prevents errors with multiprocessing
    app_settings_dir = os.path.abspath("settings.json")
    # Autostarts the autostarts
    # Finds how many autostarts there are
    launch_amount = 0
    for app in os.listdir("instances/"):
        config_file = f"instances/{app}/config.json"
        if jmod.getvalue(key=f"autostart", json_dir=config_file) == True:
            name = jmod.getvalue(key='name', json_dir=config_file)
            port = jmod.getvalue(key='port', json_dir=config_file)
            ports_taken = {}
            ports_taken.update({port: name})

    do_autostart = jmod.getvalue("do_autostart", app_settings_dir, False, dt=app_settings)
    if do_autostart is True:
        for app in os.listdir("instances/"):
            if jmod.getvalue(key=f"autostart", json_dir=config_file) == True:
                name = jmod.getvalue(key='name', json_dir=config_file)
                port = jmod.getvalue(key='port', json_dir=config_file)
                if ports_taken[port] == name: # Allows only the assigned port to the name to be used
                    print(f"Auto-Initializing project: \"{name}\" on port {port} (http://localhost:{port})")
                    logging.info(f"Auto-Initializing project: \"{name}\" on port {port}")
                    website = threading.Process(
                        target=instance.start, args=(app, True),\
                        name=f"{app}_webserver"
                        )
                    website.start()
                    pid = website.pid
                    jmod.setvalue(
                        key="pid",
                        json_dir=f"instances/{app}/config.json",
                        value=pid,
                        dt=config_dt
                    )
                else:
                    print(f"Port {port} is already taken! Can't start \"{name}\". Skipping")
                    logging.error(f"Port {port} is already taken! Can't start \"{name}\". Skipping")
                    continue

                launch_amount += 1

        if launch_amount != 0:
            print(f"AutoLaunched {launch_amount} instances...\n")
    else:
        print("Autostart is disabled. Skipping...")

    # The main loop to keep the program running
    application.run(
        keybind_listen=bool(os.environ.get("PYHOST_KEYBIND_LISTEN", True))
        )