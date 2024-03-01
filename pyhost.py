# Pyhost is a completely free and opensource project built by FriendlyFox.exe AKA https://github.com/Ames-Hub
# It is a lightweight, simple alternative for Nginx. It is built in Python and is very easy to use.
# It is mainly built for compatibility with pufferpanel, but it can be used bloody anywhere as it's just a python script
# Have fun!

# Importing modules
try:
    import multiprocessing
    import os
    import shutil
    import time
    import sys
    import datetime
    from getpass import getpass
    from library.jmod import jmod
    from library.snapshots import snapshots
    from library.data_tables import web_config_dt, app_settings
    from library.pylog import pylog
    from library.domains import pyhost_domain
except ImportError as err:
    print(
        "Failed to import required modules. Please run 'pip install -r requirements.txt' to install them.",
        "For more information, view the logs."
        )
    from library.pylog import pylog
    pylog().error("Failed to import required modules.", err)
    exit()

colours = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "purple": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "reset": "\033[0m"
}

pylogger = pylog()
# Start the logworker in a separate thread
if __name__ == "__main__":
    logman_enabled = jmod.getvalue(key="logman.enabled", json_dir="settings.json", default=True, dt=app_settings)
    if logman_enabled is True:
        from library.pylog import logman
        logworker = multiprocessing.Process(
            target=logman,
            args=()
        )
        logworker.start()
        jmod.setvalue(
            key="logman.pid",
            json_dir="settings.json",
            value=logworker.pid,
            dt=app_settings
        )

    is_linux = sys.platform == "linux" # If the OS is linux, it will be true
    is_mac = sys.platform == "darwin"
    pylogger.debug(f"OS Is Linux: {is_linux}")
    if is_linux:
        # Gets the BRAND of linux
        with open("/etc/os-release", 'r') as f:
            for line in f.readlines():
                if line.startswith("ID="):
                    linux_brand = line.replace("ID=", "").replace("\n", "")
                    break
        pylogger.debug(f"    Linux Brand: {linux_brand}")
    pylogger.debug(f"OS Is Windows: {os.name == 'nt'}")
    pylogger.debug(f"OS Is Apple: {is_mac}")
    pylogger.debug(f"os.name? : {os.name}")
    pylogger.debug(f"sys.platform? : {sys.platform}")
    if is_linux:
        pylogger.debug(f"Has elevated privileges? : {os.geteuid() == 0}")
    else:
        pylogger.debug("Has elevated privileges? : N/A")

    if is_mac:
        is_linux = False
        print(f"{colours['red']}<!-- WARNING! APPLE DEVICES ARE UNTESTED, AND NOT PLANNED FOR ON ANYTHING. -->")
        print(f"<!-- ANYTHING MAY GO WRONG, DESPITE THERE BEING NOTHING INTENTIONALLY STOPPING APPLE DEVICES FROM RUNNING PYHOST. -->{colours['white']}")
        print(f"{colours['yellow']}<!-- HERE BE DRAGONS -->{colours['white']}")
        if jmod.getvalue("first_launch", "settings.json", True, dt=app_settings) is True:
            input("Press enter to continue, and acknowledge the potential risks of running Pyhost on an Apple device. ")
            print("You will not see this message again.")
            time.sleep(5)

# Ensures all neccesary directories exist
os.makedirs("instances", exist_ok=True)
os.makedirs("logs", exist_ok=True)

if __name__ == "__main__": # Checks if the user is running the app for the first time
    pylogger.info("Pyhost logging started successfully!")
    from library.application import application
    application.clear_console()

    first_launch = jmod.getvalue("first_launch.app", "settings.json", True, dt=app_settings)
    # Done in multiple if's like this to break up the code and make it easier to read via folding/shrinking the code with VSC
    # Lets you focus on 1 section at a time this way
    if first_launch is True: # Checks if the user has backups from a previous pyhost install
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
    if jmod.getvalue("hostname", "settings.json", dt=app_settings) == -1: # Gets the hostname, as some functions (as of 21/12/2023, the webgui's JS) require it
        pyhost_domain.setdomain()

    if is_linux:
        # Gets this value should the user want to run web apps on ports below 1024 on Linux.
        try:
            with open("library/ssl/linux.pw", 'rb') as f:
                if f.read() in [b'', b' ', '', None]:
                    raise FileNotFoundError
        except FileNotFoundError:
            got_password = False
        if not got_password:
            while True:
                print("Would you like to be able to run apps on ports below 1024? (y/n)")
                yesno = input(">>> ").lower()
                if yesno not in ["yes", "y", "n", "no", "nope"]:
                    print("Invalid choice! Must be 'y' (yes) or 'n' (no)")
                    continue
                break
            while True:
                if yesno in ["y", "yes"]:
                    print(f"In that case, we will require a {colours['green']}Root Password{colours['white']}.")
                    print("This password will be stored, securely encrypted using your own personal key using cryptography in the 'linux.pw' file.")
                    print(f"{colours['cyan']}Please enter the password we should use. Type \"!cancel!\" to cancel{colours['white']}")
                    password = getpass("[Sudo] >>> ")
                    if password == "!cancel!":
                        print("Cancelled!")
                        break
                    # Tries to execute a command that requires root permissions to see if the password is correct
                    print("Please confirm your password. (Note: We cannot check this password)")
                    reconfirm = getpass("[Sudo] >>> ")
                    if reconfirm != password:
                        print("Passwords do not match!")
                        continue
                    else:
                        print("Password confirmed! Beginning encryption...")
                        # Encrypts the password
                        from library.application import keys
                        password = keys().encrypt(password)
                        # Wait a couple seconds to make it seem like it's doing something complicated.
                        # The encryption is solid, but it's also fast, so it doesn't take long to encrypt.
                        # This can make it feel like it's not doing anything, so this is just to make it feel like it is
                        # to a user who hasn't seen the code / can't program.
                        # Saves the password
                        with open("library/ssl/linux.pw", 'wb') as f:
                            f.write(password)
                        break
                else:
                    print("Skipping root setup...")
                    time.sleep(1)
                    break

    if first_launch is True:
        try:
            input("\n\nEnd of setup. Take this time to read any potentially useful information.\nPress enter to continue when you are ready.")
        except KeyboardInterrupt:
            exit()
    # The code that sets first_launch to false is now in the application's exit code.
    # application.py > application.run() > Look for code `except KeyboardInterrupt`
    # Moved there so that "first launch" help screens can be shown else where and it only says its not first launch
    # AFTER they exit the program for the first time

# Only load these here to prevent a [WinError 3] error
from library.API.Controller import controller as apicontroller
from library.application import application
from library.filetransfer import ftp
from library.instance import instance
from library.WebGUI.webgui import webcontroller

def auto_backup():
    # Gets all apps
    try:
        while True:
            try:
                time.sleep(600) # Sleep for 10 minutes
            except KeyboardInterrupt:
                exit()
            apps = os.listdir("instances/")
            for app_instance in apps:
                boundpath = jmod.getvalue(key="boundpath", json_dir=f"instances/{app_instance}/config.json")
                contentpath = jmod.getvalue(key="contentloc", json_dir=f"instances/{app_instance}/config.json")

                if boundpath == contentpath:
                    if snapshots.check_outdated(app_name=app_instance) is True:
                        snapshots.backup(
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
    print("https://github.com/Ames-Hub/pyhoster | https://github.com/Ames-hub/pyhoster/issues\n")
    print("Message from developer:\nHello! If you have any issues, let me know and I will personally help out!\n")

    # Makes an init backup for every app which has its boundpath == content path.
    # This is because auto-backups often only happen if they intentionally update the app
    # which does not always happen if the boundpath is equal to the content path
    # (as the 'update' command is half-useless in that case)

    do_autobackup = jmod.getvalue(key="do_autobackup", json_dir="settings.json", default=True, dt=app_settings)
    if do_autobackup:
        auto_backup_thread = multiprocessing.Process(
            name="auto_backup",
            target=auto_backup
        )
        auto_backup_thread.start()

    ftp_ssl_enabled = jmod.getvalue(key="ssl_enabled", json_dir="settings.json", default=True, dt=app_settings)
    # Starts the FTP server if enabled
    ftp_enabled = jmod.getvalue(key="FTP_Enabled", json_dir="settings.json", default=False, dt=app_settings)
    if ftp_enabled is True:
        FTP_Thread = multiprocessing.Process(
            target=ftp.start,
            args=(None, None, None, ftp_ssl_enabled),
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
                port = jmod.getvalue("FtpPort", "settings.json", 4035, dt=app_settings)
                print(f"Port {port} is already taken! Can't start FTP server.")
                pylogger.error(f"Port {port} is already taken! Can't start FTP server.", err)
    else:
        pylogger.info("FTP server is disabled.")

    API_Enabled = jmod.getvalue(key="api.autoboot", json_dir="settings.json", default=False, dt=app_settings)
    if API_Enabled is True:
        pylogger.info("API is Enabled. Starting.")
        try:
            apicontroller.initapi()
        except OSError as err:
            if err.errno == 13:
                port = jmod.getvalue("api.port", "settings.json", 4045, dt=app_settings)
                pylogger.error(f"Port {port} is already taken! Can't start API.", err)
                print(f"Port {port} is already taken! Can't start API.")
                exit()
            else:
                print("An unknown error occurred while starting the API. Please check the logs for more info.")
                pylogger.error("An unknown error occurred while starting the API.", err)
    else:
        pylogger.info("API is disabled.")

    # Starts WebGUI thread if webgui is enabled
    webgui_enabled = jmod.getvalue("webgui.autoboot", "settings.json", True, dt=app_settings)
    if webgui_enabled is True:
        webcontroller.run(silent_gui=-1) # It'll check in the function with -1
    else:
        pylogger.info("WebGUI is disabled.")

# Starts the session man
def tokenMan():
    from library.userman import session_json
    from library.pylog import pylog
    logs = pylog(filename="logs/sessionman.log")
    logs.info("Session manager started.")
    times_checked = 0
    try:
        while True:
            time.sleep(5) # Sleep for a second to not use too much CPU and not spam-access the file/disk
            sessions = session_json.list()
            exp_hours = jmod.getvalue(key="tokenMan.expiration_hours", json_dir="settings.json", default=24, dt=app_settings)
            exp_hours = exp_hours * 60 * 60  # Convert hours to seconds
            current_time = time.time()  # Store the current time outside the loop
            for session_key, session_data in sessions.items():
                # Checks if the session has expired
                elapsed_time = current_time - session_data['start']
                if elapsed_time > exp_hours:
                    session_json.remove(session_key)  # Token is the key
                    logs.info(f"Removed expired session token | {session_key}")
    
            times_checked += 1
            if times_checked  % 800 == 0: # 800 * 5 = 4000 seconds = 1 hour. So this will run every hour or 24 times a day assuming the program is running 24/7 at 12:00am
                logs.info(f"Checked through {times_checked} times. Logging basic info below.")
                logs.info(f"Current specific time: {datetime.datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S')}")
                logs.info(f"Current POSIX time: {current_time}")
                logs.info(f"Current expiration time: {exp_hours}")
                logs.info(f"Current session count: {len(sessions)}")
                
    except KeyboardInterrupt:
        return True

sman_enabled = jmod.getvalue("tokenMan.enabled", "settings.json", True, dt=app_settings)
if __name__ == "__main__":
    if sman_enabled is True:
        sman_thread = multiprocessing.Process(
            target=tokenMan,
            args=()
        )
        sman_thread.start()
        jmod.setvalue(
            key="tokenMan.pid",
            json_dir="settings.json",
            value=sman_thread.pid,
            dt=app_settings
        )

    # Writes a text file to library/ssl/ saying to NEVER share the private key
    if not os.path.exists("library/ssl/README_IMPORTANT.txt"):
        os.makedirs("library/ssl/", exist_ok=True)
        with open("library/ssl/README_IMPORTANT.txt", "a+") as f:
            f.write("This folder contains the SSL certificates for the webserver. DO NOT SHARE THE BLOODY ANYTHING IN HERE WITH ANYONE.\n")
            f.write("If you do, they will be able to decrypt all traffic to and from your server, and steal any data sent to it.\n")
            f.write("And if your website has an admin panel, GUESS WHO HAS ACCESS TO IT NOW? That's right! They do as they just stole the username AND password!\n")
            f.write("You should never need to touch these files, and if you do, you should know what you're doing.\n")

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
                if port == jmod.getvalue(key="api.port", json_dir=app_settings_dir, default=4045, dt=app_settings):
                    print(f"Port {port} is already taken by the API! Can't start \"{name}\". Skipping.")
                    pylogger.warning(f"Port {port} is already taken by the API! Can't start \"{name}\". Skipping.")
                    continue
                elif port == jmod.getvalue(key="webgui.port", json_dir=app_settings_dir, default=4040, dt=app_settings):
                    print(f"Port {port} is already taken by the WebGUI! Can't start \"{name}\". Skipping.")
                    pylogger.warning(f"Port {port} is already taken by the WebGUI! Can't start \"{name}\". Skipping.")
                    continue
                elif port < 1024 and is_linux is True:
                    if os.geteuid() == 0: # get_euid only works on linux. So its behind the above IF statement
                        print(f"{colours['yellow']}Skipping autostart on app '{name}' as it requires root permissions to run on port {port}, which is lower than 1024 (the lowest port we are allowed to run on)")
                        print(f"You can change the port by entering the command 'edit {name}' then selecting option 2 (port) and changing it to a number greater than 1023{colours['white']}")
                        pylogger.warning(f"Skipping autostart on app '{name}' as it requires root permissions to run on port {port}, which is lower than 1024")
                    continue
                apptype = jmod.getvalue(key='apptype', json_dir=config_file)
                if ports_taken[port] == name:
                    # Log the start of the application and start it in a new thread
                    do_ssl = "s" if jmod.getvalue(
                        key="ssl_enabled",
                        json_dir=config_file,
                        default=True,
                        dt=web_config_dt
                    ) is True else ""

                    print(f"Auto-Initializing project: \"{name}\" on port {port} (http{do_ssl}://localhost:{port})")
                    pylogger.info(f"Auto-Initializing project: \"{name}\" on port {port}")
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
                    pylogger.warning(f"Port {port} is already taken by {ports_taken[port]}! Can't start \"{name}\". "
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
