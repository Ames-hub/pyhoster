# Pyhost is a completely free and opensource project built by FriendlyFox.exe AKA https://github.com/Ames-Hub
# It is a lightweight, simple replacement for Nginx. It is built in Python and is very easy to use.
# It is mainly built for compatibility with pufferpanel, but it can be used bloody anywhere as it's just a python script
# Have fun!

# Importing modules
import datetime
import logging
import multiprocessing
import os
import shutil
import time

from library.API.Controller import controller as apicontroller
from library.application import application
from library.data_tables import web_config_dt, app_settings
from library.filetransfer import ftp
from library.instance import instance
from library.jmod import jmod
from library.WebGUI.webgui import webcontroller

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

if __name__ == "__main__": # Checks if the user is running the app for the first time
    # Checks if settings.json exists
    if os.path.exists("settings.json") is False:
        import json # Import here so that it never imports unless needed, freeing up memory.
        # Creates settings.json
        with open("settings.json", "w") as f:
            json.dump(app_settings, f, indent=4, separators=(',', ': '))

    first_launch = jmod.getvalue("first_launch", "settings.json", True, dt=app_settings)
    if first_launch is True:
        # Checks if the user has backups from a previous pyhost install
        linux = os.name != "nt" # If the OS is linux, it will be true
        if linux:
            backup_dir = f"/var/pyhoster/backups/"
        else:
            # Gets the appdata directory for the user
            appdata = os.getenv("APPDATA")
            backup_dir = f"{appdata}/pyhoster/backups/"

        if os.path.exists(backup_dir) is True:
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
                        # All vers inside the "app" folder will be formatted as "ver<version number>".
                        # This will get the app with the highest version number
                        versions = os.listdir(f"{backup_dir}/{app}")
                        highest_version = 0
                        for ver in versions:
                            if int(ver.replace("ver", "")) > highest_version:
                                highest_version = int(ver.replace("ver", ""))

                        shutil.copytree(
                            src=f"{backup_dir}/{app}/ver{highest_version}", dst=f"instances/{app}", dirs_exist_ok=True
                        )
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

def auto_backup():
    # Gets all apps
    try:
        while True:
            try:
                time.sleep(600)
            except KeyboardInterrupt:
                exit()
            apps = os.listdir("instances/")
            for app_instance in apps:
                boundpath = jmod.getvalue(key="boundpath", json_dir=f"instances/{app_instance}/config.json")
                contentpath = jmod.getvalue(key="contentloc", json_dir=f"instances/{app_instance}/config.json")

                if boundpath == contentpath:
                    if instance.is_outdated(app_name=app_instance) is True:
                        instance.backup(
                            app_name=app_instance,
                            is_interface=False,
                            do_alert=False
                        )
    except PermissionError:
        print("Permission error! Backups cannot be made. Please set your own backup directory by using")
        print("1. command 'settings'")
        print("2. option 'backups path'")
        print("3. enter the path you want to use. Pyhost must have access to it.")

main_pid = os.getpid()
if __name__ == "__main__": # Prevents errors with multiprocessing
    reset_colour = "\033[0m" # Clears any previous colour
    print(reset_colour)
    # Clears the screen and prints the welcome message
    os.system('cls' if os.name == "nt" else "clear")
    print(f"({main_pid}) Welcome to Pyhost! - A Customizable, simple to use Website Manager.")
    print("https://github.com/Ames-Hub/pyhoster\n")
    print("Message from developer:\nHello! If you have any issues, let me know and I will personally help out!\n")

    # Makes an init backup for every app which has its boundpath == content path.
    # This is because auto-backups often only happen if they intentionally update the app
    # which does not always happen if the boundpath is equal to the content path
    # (as the 'update' command is useless in that case)

    do_autobackup = jmod.getvalue(key="do_autobackup", json_dir="settings.json", default=True, dt=app_settings)
    if do_autobackup:
        auto_backup_thread = multiprocessing.Process(
            name="auto_backup",
            target=auto_backup
        )
        auto_backup_thread.start()

    ssl_enabled = jmod.getvalue(key="ssl_enabled", json_dir="settings.json", default=True, dt=app_settings)
    # Starts the FTP server if enabled
    ftp_enabled = jmod.getvalue(key="FTP_Enabled", json_dir="settings.json", default=False, dt=app_settings)
    if ftp_enabled is True:
        FTP_Thread = multiprocessing.Process(
            target=ftp.start,
            args=(None, None, None, ssl_enabled),
        ) # Certfile and private keyfile being none just gets it to generate a self-signed certificate
        try:
            FTP_Thread.start()
            jmod.setvalue(
                key="ftppid",
                json_dir="settings.json",
                value=FTP_Thread.pid,
                dt=app_settings
            )
        except OSError as err:
            if err.errno == 13:
                port = jmod.getvalue("FtpPort", "settings.json", 789, dt=app_settings)
                print(f"Port {port} is already taken! Can't start FTP server.")
                logging.error("Port 789 is already taken! Can't start FTP server.")
    else:
        logging.info("FTP server is disabled.")

    API_Enabled = jmod.getvalue(key="api.autoboot", json_dir="settings.json", default=False, dt=app_settings)
    if API_Enabled is True:
        logging.info("API is Enabled. Starting.")
        try:
            apicontroller.initapi()
        except OSError as err:
            if err.errno == 13:
                port = jmod.getvalue("api.port", "settings.json", 987, dt=app_settings)
                logging.error(f"Port {port} is already taken! Can't start API.")
                print(f"Port {port} is already taken! Can't start API.")
                exit()
            else:
                print("An unknown error occurred while starting the API. Please check the logs for more info.")
                logging.error("An unknown error occurred while starting the API.")
    else:
        logging.info("API is disabled.")

    # Starts WebGUI thread if webgui is enabled
    webgui_enabled = jmod.getvalue("webgui.autoboot", "settings.json", True, dt=app_settings)
    if webgui_enabled is True:
        webcontroller.run(silent_gui=-1) # It'll check in the function with -1
    else:
        logging.info("WebGUI is disabled.")

if __name__ == '__main__': # This line ensures the script is being run directly and not imported
    app_settings_dir = os.path.abspath("settings.json")

    # Initialize a dictionary to keep track of which ports are taken
    ports_taken = {}
    launch_amount = 0 # Counter for the number of applications launched

    # Loop over all applications in the 'instances' directory
    for app in os.listdir("instances/"):
        config_file = f"instances/{app}/config.json" # Path to the config file for each application
        # If the application is set to autostart, add its port and name to the ports_taken dictionary
        if jmod.getvalue(key=f"autostart", json_dir=config_file) is True:
            name = jmod.getvalue(key='name', json_dir=config_file)
            port = jmod.getvalue(key='port', json_dir=config_file)
            ports_taken[port] = name

    # Check if autostart is enabled in the main settings
    do_autostart = jmod.getvalue("do_autostart", app_settings_dir, False, dt=app_settings)
    if do_autostart is True:
        # If autostart is enabled, loop over all applications again
        for app in os.listdir("instances/"):
            config_file = f"instances/{app}/config.json"  # Update the config_file for each app
            # If the application is set to autostart and its port is not taken by another application, start it
            if jmod.getvalue(key=f"autostart", json_dir=config_file) is True:
                name = jmod.getvalue(key='name', json_dir=config_file)
                port = jmod.getvalue(key='port', json_dir=config_file)
                apptype = jmod.getvalue(key='apptype', json_dir=config_file)
                if ports_taken[port] == name:
                    # Log the start of the application and start it in a new thread
                    print(f"Auto-Initializing project: \"{name}\" on port {port} (http://localhost:{port})")
                    logging.info(f"Auto-Initializing project: \"{name}\" on port {port}")
                    if apptype == application.types.webpage():
                        # If the application is a webpage, start it with the 'start' method of the 'instance' module
                        website = multiprocessing.Process(
                            target=instance.start, args=(app, True),
                            name=f"{app}_webserver"
                            )
                        website.start()
                        pid = website.pid
                    elif apptype == application.types.WSGI():
                        # If the application is a WSGI application start it with the 'start' method of the 'instance' module
                        wsgi = multiprocessing.Process(
                            target=instance.start, args=(app, True),
                            name=f"{app}_wsgi"
                            )
                        wsgi.start()
                        pid = wsgi.pid
                    # Save the process ID of the application to its config file
                    jmod.setvalue(
                        key="pid",
                        json_dir=f"instances/{app}/config.json",
                        value=pid,
                        dt=web_config_dt
                    )
                else:
                    # If the port is already taken, log an error and skip this application
                    print(f"Port {port} is already taken by {ports_taken[port]}! Can't start \"{name}\". Skipping")
                    logging.error(f"Port {port} is already taken by {ports_taken[port]}! Can't start \"{name}\". "
                                  f"Skipping")
                    continue

                launch_amount += 1

        if launch_amount != 0:
            # If any applications were launched, log the total number
            print(f"AutoLaunched {launch_amount} instances...\n")
    else:
        # If autostart is disabled, log a message and end the script
        print("Autostart is disabled. Skipping…")

    # The main loop to keep the program running
    application.run(
        keybind_listen=bool(os.environ.get("PYHOST_KEYBIND_LISTEN", True))
        )
