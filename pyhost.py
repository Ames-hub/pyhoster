# PYHOST
# Pyhost is a completely free and opensource project built by FriendlyFox.exe AKA https://github.com/Ames-Hub
# It is a lightweight, simple replacement for Nginx. It is built in Python and is very easy to use.
# It is mainly built for compatibility with pufferpanel, but it can be used bloody anywhere as its just a python script
# Have fun!

# Importing modules
import os, logging, datetime, multiprocessing as threading, shutil, time
from library.jmod import jmod
from library.application import application
from library.instance import instance
from library.data_tables import config_dt

os.system('cls' if os.name == "nt" else "clear")
main_pid = os.getpid()
print(f"({main_pid}) Welcome to Pyhost! - A lightweight, simple replacement for Nginx.")
print("https://github.com/Ames-Hub/pyhost\n")
print("Message from developer:\nHello! If you have any issues, let me know and I will personally help out!\n")

# Ensures all neccesary directories exist
os.makedirs("instances", exist_ok=True)
os.makedirs("logs", exist_ok=True)

filename = str(datetime.date.today().strftime("%Y-%m-%d"))
# Sets up logging
logging.basicConfig(
    # Gets a readable datetime format for the log filename
    filename=f"logs/{filename}.log",
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.basicConfig(
    # Gets a readable datetime format for the log filename
    filename=f"logs/{filename}.log",
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)

logging.info("Pyhost logging started successfully!")

def sync_content():
    try:
        while True:
            logging.info("Updating apps")
            for app in os.listdir(os.path.abspath("instances/")):
                # Gets the boundpath
                external_boundpath = jmod.getvalue(
                    key="boundpath",
                    json_dir=str(os.path.abspath(f"instances/{app}/config.json")),
                    default=None,
                    dt=config_dt(app),
                )

                if external_boundpath is not None:  # Check if external_boundpath is not None
                    internal_boundpath = jmod.getvalue(
                        key="contentloc",
                        json_dir=str(os.path.abspath(f"instances/{app}/config.json")),
                        default=None,
                        dt=config_dt(app),
                    )
                    # Checks each file in the external path against the internal path, and updates the file in
                    # Internal with the one in external if they do not match.
                    for ext_file in os.listdir(external_boundpath):
                        extbp = external_boundpath
                        intbp = internal_boundpath
                        if ext_file in os.listdir(intbp):
                            # Handles out-of-date files. Doesn't handle new files created or deleted.
                            with open(f"{extbp}/{ext_file}", "r") as extf:
                                extf_content: str = extf.read()
                            # Compares against the internal copy.
                            with open(f"{intbp}/{ext_file}", "r") as intf:
                                intf_content: str = intf.read()

                            if extf_content != intf_content:
                                # Updates the file.
                                os.remove(f"{intbp}/{ext_file}")
                                shutil.copyfile(
                                    src=f"{extbp}/{ext_file}",
                                    dst=f"{intbp}/{ext_file}"
                                )
                        elif ext_file not in os.listdir(intbp):
                            # If the external file is not in the internal directory, copy it across.
                            shutil.copyfile(
                                src=f"{extbp}/{ext_file}",
                                dst=f"{intbp}/{ext_file}"
                            )

                    # Handles files that exist in intbp but not extbp by deleting them.
                    for int_file in os.listdir(internal_boundpath):
                        extbp = external_boundpath
                        intbp = internal_boundpath
                        if int_file not in os.listdir(extbp):
                            # Delete the internal file as it doesn't exist externally.
                            os.remove(f"{intbp}/{int_file}")
                else:
                    logging.warning(f"External boundpath is None for app: {app}")
    except Exception as err:
        pass

if __name__ == '__main__': # Prevents errors with multiprocessing
    # Autostarts the autostarts
    # Finds how many autostarts there are
    launch_amount = 0
    thread_arr = []
    for app in os.listdir("instances/"):
        config_file = f"instances/{app}/config.json"
        if jmod.getvalue(key=f"autostart", json_dir=config_file) == True:
            name = jmod.getvalue(key='name', json_dir=config_file)
            port = jmod.getvalue(key='port', json_dir=config_file)
            print(f"Auto-Initializing project: \"{name}\" on port {port}")
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
                dt=config_dt(app)
            )

            launch_amount += 1

    # Starts a thread to keep boundpaths up-to-date with content paths.
    syncfile_thread = threading.Process(
        target=sync_content,
        name="filesync",
    )
    syncfile_thread.start()

    if launch_amount != 0:
        print(f"AutoLaunched {launch_amount} instances...\n")

    # The main loop to keep the program running
    application.run(
        keybind_listen=bool(os.environ.get("PYHOST_KEYBIND_LISTEN", True))
        )