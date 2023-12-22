import os, multiprocessing as mp, json, time
if os.name == "nt":
    import ctypes
try:
    from .data_tables import app_settings, web_config_dt, wsgi_config_dt
    from .filetransfer import ftp
    from .warden import warden
    from .jmod import jmod
    from .userman import userman
    from .API.Controller import controller as apicontroller
    from .WebGUI.webgui import webcontroller
except ImportError as err:
    print("Hello! To run Pyhost, you must run the file pyhost.py located in this projects root directory, not this file.\nThank you!")
    from library.pylog import pylog
    pylog().error(f"Import error in {__name__}", err)
import sys, subprocess, hashlib, base64
from cryptography.fernet import Fernet

from .pylog import pylog
pylogger = pylog()

root_dir = os.getcwd()
FTP_Enabled = bool(jmod.getvalue("FTP_Enabled", "settings.json", dt=app_settings, default=False))

colours = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "purple": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "orange": "\033[38;5;208m",
}

def getkwrd(keywords, text, default=None):
    try:
        text = str(text).lower()
        keywords = [str(keyword).lower() for keyword in keywords]
    except ValueError as err:
        pylogger.warning(f"Error: Kward bad type. Error: {err}")

    for keyword in keywords:
        index = text.find(keyword + ":")
        if index != -1:
            text = text[index + len(keyword) + 1:]

            start_quote = text[0]

            singlequote = start_quote == "'"
            if singlequote:
                end_quote = text.find("'", 1)
            elif not singlequote:
                end_quote = text.find('"', 1)
            else:
                raise IndexError("No closing quote was found for a keyword arg!")

            value = text[1:end_quote]
            return value

    # Return Default if none of the keywords are found
    return default

class keys:
    '''
    Treat the key this generates as a password, ofc.
    '''
    def __init__(self, keypath="library/ssl/linuxpw.key"):
        # Define key_file attribute here
        self.keypath = keypath

        # Try to load the key from the file, generate a new one if it fails
        loaded_Key = self.load()
        self.private_key = loaded_Key if loaded_Key != None else self.generate_private_key()
        self.cipher_suite = Fernet(self.private_key)
        pylogger.info("Starting encryption session...")

    def generate_private_key(self):
        # Collect various system-related data to create a more random seed
        seed_data = os.urandom(128)  # Using os.urandom for 'randomness'
        # Adds extra randomness
        seed_data += str(os.getpid()).encode()
        seed_data += str(os.times()).encode()
        seed_data += str(os.uname()).encode()
        seed_data += str(time.time()).encode()

        # Hash the collected data to create a secure key
        hashed_key = hashlib.sha256(seed_data).digest()

        # Encode the key to base64 to make it compatible with Fernet
        encoded_key = base64.urlsafe_b64encode(hashed_key)

        # Save the key to a file
        pylogger.info("Generating new private key...")
        self.save(encoded_key)
        return encoded_key

    def encrypt(self, text):
        # Encrypt the text using the private key
        pylogger.info("Encrypting text...")
        encrypted_text = self.cipher_suite.encrypt(text.encode())
        return encrypted_text

    def decrypt(self, encrypted_text):
        # Decrypt the text using the private key
        pylogger.info("Decrypting text...")
        decrypted_text = self.cipher_suite.decrypt(encrypted_text).decode()
        return decrypted_text

    def save(self, private_key):
        # Save the private key to a file
        pylogger.info("Saving private key...")
        os.makedirs(os.path.dirname(self.keypath), exist_ok=True)
        with open(self.keypath, "wb") as f:  # Open the file in binary mode
            f.write(private_key)

    def load(self):
        try:
            with open(self.keypath, "rb") as f:  # Open the file in binary mode
                private_key = f.read().strip()
        except FileNotFoundError:
            private_key = self.generate_private_key()

        pylogger.info("Loading private key...")
        return private_key

def idle_mode_printer():
    while True:
        webgui_running = jmod.getvalue("webgui.running", "settings.json", dt=app_settings, default=False)
        api_running = jmod.getvalue("api.running", "settings.json", dt=app_settings, default=False)
        ftp_running = jmod.getvalue("FTP_Running", "settings.json", dt=app_settings, default=False)
        webgui_pid = jmod.getvalue("webgui.pid", "settings.json", dt=app_settings, default=None)
        api_pid = jmod.getvalue("api.pid", "settings.json", dt=app_settings, default=None)
        ftp_pid = jmod.getvalue("ftppid", "settings.json", dt=app_settings, default=None)
        webgui_port = jmod.getvalue("webgui.port", "settings.json", dt=app_settings, default=None)
        api_port = jmod.getvalue("api.port", "settings.json", dt=app_settings, default=None)
        ftp_port = jmod.getvalue("FTP_Port", "settings.json", dt=app_settings, default=None)

        instances_list = ""
        for instance in os.listdir("instances/"):
            with open(f"instances/{instance}/config.json", 'r') as config_file:
                config_data = json.load(config_file)
            if config_data.get("running") == True:
                instances_list += f"{instance} - {colours['green']}Running{colours['white']}\n"
                instances_list += f"    Port: {config_data.get('port')}\n"
                instances_list += f"    PID: {config_data.get('pid')}\n\n"
            else:
                instances_list += f"{instance} - {colours['red']}Not Running{colours['white']}\n"

        # FTP Status
        ftp_status = ""
        if ftp_running == True:
            ftp_status += f"FTP Server - {colours['green']}Running{colours['white']}\n"
            ftp_status += f"    Port: {ftp_port}\n"
            ftp_status += f"    PID: {ftp_pid}\n\n"
        else:
            ftp_status += f"FTP Server - {colours['red']}Not Running{colours['white']}\n"

        # WebGUI Status
        webgui_status = ""
        if webgui_running == True:
            webgui_status += f"WebGUI - {colours['green']}Running{colours['white']}\n"
            webgui_status += f"    Port: {webgui_port}\n"
            webgui_status += f"    PID: {webgui_pid}\n\n"
        else:
            webgui_status += f"WebGUI - {colours['red']}Not Running{colours['white']}\n"

        # API Status
        api_status = ""
        if api_running == True:
            api_status += f"API - {colours['green']}Running{colours['white']}\n"
            api_status += f"    Port: {api_port}\n"
            api_status += f"    PID: {api_pid}\n\n"
        else:
            api_status += f"API - {colours['red']}Not Running{colours['white']}\n"

        screen = f'''
<!-------- {application.rainbowify_text('PYHOST')} --------!>
Pyhost is currently running in the background.
To exit IDLE mode, press enter.

{application.rainbowify_text('INSTANCES')}
---------------------
{instances_list}
---------------------

{ftp_status}
{webgui_status}
{api_status}
'''
        os.system("cls" if os.name == "nt" else "clear")
        print(screen)
        time.sleep(0.5)

class application:

    def is_root():
        if os.name == 'nt':  # If the system is Windows
            try:
                # ctypes.windll.shell32.IsUserAnAdmin() returns True if the script is run as admin
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            except:
                return False
        else:  # If the system is Unix-like
            # os.geteuid() returns 0 if the script is run as root
            return os.geteuid() == 0

    def elevate(ask_msg="To do this, We need your Root Password.\nWe will only save this data for later use if you Ok it.\n\n>>> "):
            """
            Elevates the script to run with root privileges on Linux.

            Args:
                ask_msg (str, optional): Message to prompt the user for the root password. Defaults to a predefined message.

            Raises:
                subprocess.CalledProcessError: If there is an error while running the command with sudo.

            Notes:
                - This function is only available on Linux.
                - On Windows, administrative privileges are not required.
            """
            # Elevate the script
            if sys.platform == 'linux':
                if not application.is_root():
                    print('Elevating script...')
                    # Prompt user for password input
                    application.clear_console()
                    password = input(ask_msg)
                    while True:
                        save_pw = input("Do you want to save this password for later use? (y/n)\n>>> ").lower()
                        if save_pw == "y":
                            jmod.setvalue(
                                key="linux.password",
                                json_dir="settings.json",
                                value=keys().encrypt(password),
                                dt=app_settings
                            )
                            break
                        elif save_pw == "n":
                            save_pw = False
                            break
                    # Command to run as root
                    command = 'python3.10 ' + sys.argv[0]  # Adjust this line based on your specific requirements
                    
                    # Use subprocess to run the command with sudo
                    try:
                        subprocess.run(['sudo', '-S', command], input=password.encode(), check=True, text=True)
                        exit() # Exit the non-root script
                    except subprocess.CalledProcessError as e:
                        print(f"Error: {e}")
                        sys.exit()
            else:
                print("This feature is only available on Linux! On windows, We do not need Admin to do what we need.")

    def run(keybind_listen: bool = True):
        application.running = True
        if FTP_Enabled == True:
            time.sleep(1) # Give the FTP server time to start up

        def help_msg():
            print("Available Commands:")
            if bool(os.environ.get("PYHOST_KEYBIND_LISTEN",True)) == False:
                print("NONE: Input has been disabled. How did you even get here?")
            else:
                print("idle: Displays information about pyhost and its instances while it is left 'idle.'")
                print("cls: Clears the screen")
                print("enter: Enters an app's GUI")
                print("ftp: Enters the FTP GUI")
                print("warden: Enters the Warden GUI")
                print("userman: Enters the User Management GUI")
                print("api: Enters the API Command Line Interface")
                print("gui: Opens the web GUI")
                print("webgui: Enters the web GUI")
                print("pyhost: Opens the settings menu")
                print("create: Creates a new app\n")

                print("Information: <arg_name> = Keyword information. eg, port:'80'. An * simply means it is required.")
                print("Entering a key-word like <key>:<value> will set the value of the key to the value. Eg, port:'80'")
                print("Value must always be surrounded in quotation marks.")
                print("-- Main Commands --")                
                print("webcreate: Creates a new website app")
                print("`webcreate *<app_name> port:'80' desc:'a cool app' autostart:'True or False' boundpath:'C:/users/ME/desktop/myCoolWebsitesContent/'`")
                print("wsgicreate: Creates a new WSGI app")
                print("`wsgicreate *<app_name> port:'80' desc:'a cool app' autostart:'True or False' boundpath:'C:/users/ME/desktop/cool_app.py'`")
                print("delete: Deletes an app")
                print("`delete *<app_name>`\n")

                print("start: Starts an app")
                print("edit: Edits an app")
                print("restart: Turns off then on an app")
                print("stop: Stops an app")
                print("update: Updates an app")
                print("rollback: Rollback to latest backup of an app or an earlier snapshot!")
                print("help: Displays this message")

        from .instance import instance
        try:
            while application.running is True:
                if keybind_listen == True:
                    cmd: str = str(input("Enter a command: "))
                    text = cmd
                    cmd = cmd.lower().split(" ")[0]
                    arguments = text.split(" ")[1:] # Gets all arguments after the command
                    has_args = False if len(text.split(" ")) == 1 else True
                    # Begins listening for create, delete, edit, etc commands
                    pylogger.info("New command entered! Debug Info:")
                    pylogger.info(f"Command: {cmd} | Text: {text} | Has Args: {has_args}")
                    if has_args == True:
                        app_name_arg = text.split(" ")[1]
                    if cmd == "create":
                        print("Please specify if you want to create a website or a WSGI app.")
                        print("webcreate: Creates a new website app")
                        print("wsgicreate: Creates a new WSGI app")
                    elif cmd == "webcreate" or cmd == "createweb":
                        if not has_args:
                            instance.create_web()
                        else:
                            instance.create_web(
                                app_name=app_name_arg,
                                port=getkwrd(["port", "gateway", "gate"], text, 80),
                                do_autostart=getkwrd(["autostart", "do_start"], text, True),
                                boundpath=getkwrd(["boundpath", "path"], text, None),
                                app_desc=getkwrd(["desc", "description"], text, default="An app hosted by Pyhost."),
                            )
                    elif cmd == "wsgicreate" or cmd == "createwsgi":
                        print(colours["orange"]+"Note: WSGI server's are currently in open alpha and may not work as expected."+colours["white"])
                        if not has_args:
                            instance.create_wsgi()
                        else:
                            instance.create_wsgi(
                                app_name=app_name_arg,
                                port=getkwrd(["port", "gateway", "gate"], text, 80),
                                do_autostart=getkwrd(["autostart", "do_start"], text, True),
                                boundpath=getkwrd(["boundpath", "path"], text, None),
                                app_desc=getkwrd(["desc", "description"], text, default="An app hosted by Pyhost."),
                            )
                    elif cmd == "delete":
                        if has_args == False:
                            instance.delete(is_interface=True)
                        else:
                            instance.delete(
                                app_name=app_name_arg,
                                ask_confirmation=True,
                            )
                    elif cmd == "edit":
                        if has_args == False:
                            instance.edit()
                        else:
                            instance.edit(
                                app_name=app_name_arg,
                                is_interface=False
                            )
                    elif cmd == "start":
                        if not has_args:
                            instance.start_interface(is_interface=True)
                        else:
                            instance.start_interface(
                                app_name=app_name_arg,
                                is_interface=False
                            )
                    elif cmd == "idle":
                        application.idle()
                        continue
                    elif cmd == "status":
                        if has_args:
                            instance.get_status(app_name=app_name_arg)
                        else:
                            instance.get_status(is_interface=True)
                    elif cmd == "ftp":
                        ftp.enter()
                        # Read doc string for more info. as a summary though,
                        # ftp.enter simply enters a GUI where logs are visible, server details are visible, etc.
                    # The command 'enter' is being processed
                    elif cmd in ["users", "userman", "usermanagement", "user"]:
                        userman.enter()
                    elif cmd == "enter":
                        if has_args:
                            enter_item = app_name_arg
                            # If it has args, the first arg is the item to enter.
                            try:
                                app_name = arguments[1]
                            except IndexError: # May not have an app name provided. Must prompt for it
                                app_name = None
                        else:
                            enter_item = input("Enter the item you want to enter\n1. FTP\n2. Warden\n3. users\n4. API\n>>> ").lower()
                            app_name = None

                        if enter_item == "ftp":
                            ftp.enter()
                        elif enter_item == "warden":
                            warden.enter(app_name)
                        elif enter_item == "users":
                            userman.enter()
                        elif enter_item == "api":
                            apicontroller.enter()
                    elif cmd == "api":
                        apicontroller.enter()
                    elif cmd == "gui":
                        print("Opening the web GUI...")
                        webcontroller.open_gui()
                    elif cmd == "webgui":
                        webcontroller.enter()
                    elif cmd == "warden":
                        warden.enter(app_name)
                    elif cmd == "restart":
                        if has_args == False:
                            instance.restart(is_interface=True)
                        else:
                            instance.restart(
                                app_name=app_name_arg,
                                is_interface=False
                            )
                    elif cmd == "stop":
                        if has_args == False:
                            instance.stop_interface()
                        else:
                            instance.stop(app_name=app_name_arg)
                    elif cmd == "update":
                        if has_args == False:
                            instance.update(is_interface=True)
                        else:
                            instance.update(app_name=app_name_arg, is_interface=False)
                    elif cmd == "rollback":
                        if not has_args:
                            instance.rollback(is_interface=True)
                        else:
                            rollback_ver = getkwrd(["ver", "version"], text=text)

                            instance.rollback(
                                app_name=app_name_arg,
                                is_interface=False,
                                rollback_ver=rollback_ver,
                                )
                    elif cmd == "backup":
                        if not has_args:
                            instance.backup(is_interface=True)
                        else:
                            instance.backup(app_name=app_name_arg, is_interface=False, do_alert=True)
                    elif cmd == "help":
                        help_msg()
                    elif cmd == "cls" or cmd == "clear":
                        application.clear_console()
                    elif cmd == "":
                        pass # Idk why, but it takes 1 press of enter to have the message appear. weird
                    elif cmd == "pyhost" or cmd == "settings":
                        application.settings(is_interface=True)
                        # Starts settings configuration
                    elif cmd in ("exit", "quit", "stop", "end"):
                        while True:
                            print("Are you sure you want to exit? y/n")
                            answer = input(">>> ").lower()
                            if answer == "y":
                                do_exit = True
                                break
                            elif answer == "n":
                                do_exit = False
                                break
                            else:
                                print("Invalid choice. y/n only.")

                        if do_exit:
                            raise KeyboardInterrupt # Raises a KeyboardInterrupt to exit the program

                    else:
                        print("Invalid command. Please try again or do `help`")
        except KeyboardInterrupt:
            application.running = False
            # Sets all the JSON file's running key to False
            from .jmod import jmod
            dotdotdot = "...\n" if not jmod.getvalue("logman.enabled", "settings.json", True, app_settings) else ""
            print(f"{dotdotdot}Exit signal received: Program is now exiting.")
            pylogger.info("Exit signal received: Program is now exiting.")

            print("Shutting down all web instances...")
            # Shuts down all the threads that run the webservers
            try:
                for app in os.listdir("instances/"):
                    config_path = os.path.abspath(f"instances/{app}/config.json")
                    with open(config_path, 'r') as config_file:
                        config_data = json.load(config_file)
                    pid = config_data.get("pid")

                    # Terminate the web server process gracefully.
                    os.kill(pid, 2)
                    # signal 2 == CTRL + C
            except Exception as err:
                pylogger.error(f"Error stopping thread: {err}", err)
            print("All web instances have been shut down.")

            # Sets the API to not running
            if jmod.getvalue("api.running", "settings.json", dt=app_settings):
                try:
                    os.kill(jmod.getvalue("api.pid", "settings.json", dt=app_settings), 2)
                    os.kill(jmod.getvalue("api.timeout_pid", "settings.json", dt=app_settings), 2)
                except:
                    try:
                        os.kill(jmod.getvalue("api.pid", "settings.json", dt=app_settings), 9)
                        os.kill(jmod.getvalue("api.timeout_pid", "settings.json", dt=app_settings), 9)
                    except:
                        pass

            print("Stopping Token manager...")
            sman_pid = jmod.getvalue(
                key="tokenMan.pid",
                json_dir="settings.json",
                dt=app_settings,
                default=None
            ) 
            if sman_pid != None:
                try:
                    os.kill(sman_pid, 2)
                except:
                    try:
                        os.kill(sman_pid, 9)
                    except:
                        pass
                jmod.setvalue(
                    key="tokenMan.pid",
                    json_dir="settings.json",
                    value=None,
                    dt=app_settings,
                )

            print("Stopping the API if it was running...")
            jmod.setvalue(
                key="api.running",
                json_dir="settings.json",
                value=False,
                dt=app_settings
            )
            # Kill the API process
            try:
                os.kill(jmod.getvalue("api.pid", "settings.json", dt=app_settings), 2)
                os.kill(jmod.getvalue("api.timeout_pid", "settings.json", dt=app_settings), 2)
            except:
                try:
                    os.kill(jmod.getvalue("api.pid", "settings.json", dt=app_settings), 9)
                    os.kill(jmod.getvalue("api.timeout_pid", "settings.json", dt=app_settings), 9)
                except:
                    pylogger.info("Failed to kill API process. It may have already been killed.")
            jmod.setvalue(
                key="api.pid",
                json_dir="settings.json",
                value=None,
                dt=app_settings
            )
            jmod.setvalue(
                key="api.timeout_pid",
                json_dir="settings.json",
                value=None,
                dt=app_settings
            )

            print("Stopping WebGUI if it was running...")
            # Kill the WebGUI process
            webcontroller.stopgui()
            jmod.setvalue(
                key="webgui.pid",
                json_dir="settings.json",
                value=None,
                dt=app_settings
            )

            print("Setting all instance configs to not running...")
            os.makedirs("instances", exist_ok=True)
            for app in os.listdir("instances/"):
                jmod.setvalue(
                    key="running",
                    json_dir=f"instances/{app}/config.json",
                    value=False,
                    dt=web_config_dt
                )
            print("All instance configs have been set to not running.")

            # Sets all PID's to None
            print("Setting all instance PID's to None...")
            for app in os.listdir("instances/"):
                jmod.setvalue(
                    key="pid",
                    json_dir=f"instances/{app}/config.json",
                    value=None,
                    dt=web_config_dt
                )
            print("All instance PID's have been set to None.")

            print("Shutting down FTP if its online...")
            try:
                ftp.stop()
            except:
                pass

            if jmod.getvalue("first_launch.app", "settings.json", True, dt=app_settings) == True:
                print("Remembering it is no longer your first time using PyHost.")
                jmod.setvalue(
                    key="first_launch.app",
                    json_dir="settings.json",
                    value=False,
                    dt=app_settings
                )

            # Wait until logging queue is empty to prevent data loss
            print("Stopping Log Worker...")
            logman_pid = jmod.getvalue(
                key="logman.pid",
                json_dir="settings.json",
                dt=app_settings,
                default=None
            )
            try:
                os.kill(logman_pid, 2)
            except:
                try:
                    os.kill(logman_pid, 9)
                except:
                    pass
            jmod.setvalue(
                key="logman.pid",
                json_dir="settings.json",
                value=None,
                dt=app_settings,
            )
            print("Log Worker has been stopped.")
            print("Thank you for choosing Pyhost!")
            print("Exiting...")
            exit()

    def idle():
        '''
        This function displays information about pyhost and its instances while it is left 'idle' and running in the background.
        Must be triggered manually. its mainly for aesthetic

        Looks best when the terminal is capable of displaying colours and clearing the screen.
        (Which, surprisingly, some aren't.)
        '''

        idle_printer = mp.Process(target=idle_mode_printer, daemon=True)
        idle_printer.start()
        input() # It will wait here until enter is pressed
        idle_printer.kill()
        print("Exiting IDLE mode... Welcome back to the main menu!")

    def rainbowify_text(text):
        '''
        This function takes a string and rainbowifies it.
        '''
        rainbow = [
            colours["red"],
            colours["orange"],
            colours["yellow"],
            colours["green"],
            colours["blue"],
            colours["purple"],
        ]
        rainbow_text = ""
        for i, char in enumerate(text):
            rainbow_text += rainbow[i % len(rainbow)] + char
        return rainbow_text+colours["white"]

    def clear_console():
        print("Hello, if you see this message, that means clearing the console is not supported in your terminal (such as pufferpanel terminal).")
        print("So as a solution, we printed 100 lines of nothing to make it look like we cleared the console. :)")
        for i in range(100):
            print("\n")
        os.system("cls" if os.name == "nt" else "clear")
    class datareqs:
        def get_name():
            '''Get the name for an app. Returns the name of the app.'''
            while True:
                try:
                    print("Type Cancel to cancel creation.")
                    app_name: str = str(input("What is the name of the app? TEXT : "))
                    if app_name.lower() == "cancel":
                        print("Cancelled!")
                        return True
                    assert app_name.lower() != "create", "The name cannot be 'create'!" # Prevents the app from being named create as it is a reserved word

                    # Makes sure the app name is valid and can be made into a directory folder
                    assert not app_name.startswith(" "), "The name cannot start with a space!"
                    assert not app_name.endswith(" "), "The name cannot end with a space!"
                    assert "." not in app_name, "The name cannot have a period!"
                    assert "/" not in app_name and "\\" not in app_name, "The name cannot contain a slash!"
                    assert "_" not in app_name, "The name cannot contain an underscore!"
                    assert "-" not in app_name, "The name cannot contain a dash!"
                    assert ":" not in app_name, "The name cannot contain a colon!"
                    assert app_name != "", "The name cannot be blank!"
                    
                    if app_name in os.listdir("instances/"):
                        raise AssertionError("The name cannot be the same as an existing app!")
                    
                    break
                except AssertionError as err: # Forces the name to be valid
                    print(str(err))
                    continue

            return app_name

        def get_desc(required=False):
            while True:
                try:
                    print("\nInstructions: <nl> = new line")
                    app_desc: str = str(input("What is the app's description? TEXT (optional) : "))
                    if app_desc.lower() == "cancel":
                        print("Cancelled!")
                        return True
                    assert type(app_desc) == str, "The description must be a string!"
                    if not required:
                        if app_desc == "":
                            app_desc = "An app hosted by Pyhost."
                    else:
                        assert app_desc != "", "The description cannot be blank!"
                    app_desc.replace("<nl>", "\n") # Replaces <nl> with a new line
                    break
                except AssertionError as err: # Forces the description to be valid
                    print(str(err))
                    continue
            return app_desc

        def get_port():
            linux = os.name != "nt"
            while True:
                try:
                    port: int = input("What port should the app run on? NUMBER (Default: 80) : ")
                    if str(port).lower() == "cancel":
                        print("Cancelled!")
                        return True
                    if str(port) == "":
                        port = 80 if not linux else 1024
                    assert type(int(port)) is int, "The port must be an integer!"
                    port = int(port)
                    assert port > 0 and port < 65535, "The port must be between 0 and 65535!"
                    if linux:
                        ran_root = os.geteuid() == 0 # Detects if the program was ran as root
                        if not ran_root:
                            assert port > 1024, f"{colours['red']}The port must be above 1024 as all ports below are reserved by Linux! To fix this, run the program as root! (or with higher privileges){colours['white']}"
                        else:
                            print("We can make this app, but if it is to ever be ran we need ROOT privileges!")
                            is_ok = input("Continue anyway? (y/n)\n>>> ").lower()
                            if is_ok == "y":
                                break
                            elif is_ok == "n":
                                print("\nRetrying...")
                                continue
                            else:
                                print("Invalid choice!")
                                continue
                    break
                except (AssertionError, ValueError) as err: # Forces the port to be valid
                    print(str(err))
                    continue

            return port

        def get_boundpath(
            message, return_default=None,
            inp_text="What is the full path to the app's content? TEXT (blank for no external binding) : "):
            while True:
                try:
                    print(message)
                    boundpath: str = str(input(inp_text))
                    if str(boundpath).lower() == "cancel":
                        print("Cancelled!")
                        return True
                    elif boundpath == "cls":
                        os.system("cls" if os.name == "nt" else "clear")
                        continue
                    elif boundpath != "":
                        assert os.path.exists(boundpath), "The path must exist and be absolute!"
                        assert os.path.isabs(boundpath), "The path must be absolute! (absolute: starting from root directory such as C:/)"
                        break
                    else:
                        boundpath = return_default
                except AssertionError as err: # Forces the path to be valid and absolute
                    print(str(err))
                    continue
            return boundpath

        def get_hostname():
            while True:
                try:
                    hostname: str = str(input("What is the hostname of the app? TEXT (blank for localhost) : "))
                    if hostname.lower() == "cancel":
                        print("Cancelled!")
                        return True
                    elif hostname == "":
                        hostname = "localhost"

                    assert "." in hostname, "The hostname must contain a period!"
                    assert hostname != "", "The hostname cannot be blank!"
                    assert all(c.isalnum() or c == "." for c in hostname), "The hostname must only contain letters, numbers, and periods!"
                    assert not hostname.startswith("."), "The hostname cannot start with a period!"
                    break
                except AssertionError as err:
                    print(str(err))
                    continue
            
            return hostname
    class types:
        def webpage():
            return "WEBPAGE"
        def WSGI():
            return "WSGI"

    class settings():
        def __init__(self, is_interface=False) -> None:
            self.is_interface = is_interface
            self.settings_dir = os.path.abspath("settings.json")

            if is_interface:
                acceptable_choices = {
                    "exit": "Ends the settings edit session.",
                    "help": "Gives information on commands. Its this menu here",
                    "do autostart": "Set if we look for autostart apps on initialization. BOOL",
                    "send 404 page": "Toggle if we send the default.html aka '404' page\nfor when an app has no index or good place to route to. BOOL",
                    "backups path": "Set the path to where backups are stored. TEXT",
                    "autobackup": "Toggle if we autobackup a snapshot of the app. BOOL",
                    "api autoboot": "Toggle if the API Autoboot is enabled. BOOL",
                }

                def help_msg():
                    print("\nHELP MENU / COMMANDS LIST")
                    for command in acceptable_choices.keys():
                        print(f"{command}: {acceptable_choices[command]}")
                    else:
                        print("\n")
                while True:
                    try:
                        print("PyHost: The website instance management tool.")
                        print("Settings menu. Type help for more information")
                        cmd = input(">>> ").lower()
                        assert cmd in acceptable_choices.keys()
                    except AssertionError:
                        print("Invalid command option")
                        continue

                    if cmd == "exit":
                        print("Exiting settings edit session.")
                        return
                    elif cmd == "help":
                        help_msg()
                    elif cmd == "do autostart":
                        self.do_autostart(is_interface=True)
                    elif cmd == "send 404 page":
                        self.send_404_page(is_interface=True)
                    elif cmd == "backups path":
                        self.backups_path(is_interface=True)
                    elif cmd == "autobackup":
                        self.autobackup(is_interface=True)
                    elif cmd == "api autoboot":
                        self.api_enabled(is_interface=True)

        def do_autostart(self, state:bool=True, is_interface:bool=False):
            if is_interface:
                while True:
                    try:
                        answer = input("Should we autostart apps? y/n : ").lower()
                        assert answer == "y" or answer == "n"
                    except:
                        print("Invalid choice")

                    state = True if answer == "y" else False
                    break
            jmod.setvalue(
                key="do_autostart",
                json_dir=self.settings_dir,
                value=state,
                dt=app_settings
            )
            if is_interface:
                print("Turned off autostarts." if state == False else "Turned on Autostarts.")
            
            pylogger.info("Turned off autostarts." if state == False else "Turned on Autostarts.")

        def send_404_page(self, state:bool=True, is_interface:bool=False):
            if is_interface:
                while True:
                    try:
                        answer = input("Should we send the 404 page for apps with no index? y/n : ").lower()
                        assert answer == "y" or answer == "n"
                    except:
                        print("Invalid choice")

                    state = True if answer == "y" else False
                    break
            
            jmod.setvalue(
                key="send_404_page",
                json_dir=self.settings_dir,
                value=state,
                dt=app_settings
            )
            if is_interface:
                print("Turned off the 404 Page." if state == False else "Turned on the 404 Page.")
            
            pylogger.info("Turned off the 404 Page." if state == False else "Turned on the 404 Page.")
            print("\nPlease restart the app at the earliest convenient time to have changes take effect\n")

        def autobackup(self, enabled=None, is_interface=True):
            '''Toggle if we autobackup a snapshot of the app before updating'''
            if is_interface or enabled==None:
                while True:
                    try:
                        answer = input("Should we autobackup apps automatically? y/n : ").lower()
                        assert answer == "y" or answer == "n"
                    except:
                        print("Invalid choice. 'y' or 'n' only")

                    enabled = True if answer == "y" else False
                    break
            
            jmod.setvalue(
                key="do_autobackup",
                json_dir=self.settings_dir,
                value=enabled,
                dt=app_settings
            )
            print("Turned off autobackups." if enabled == False else "Turned on autobackups.")
        
        def backups_path(self, path=None, is_interface=False):
            if is_interface:
                while True:
                    try:
                        print("\nPlease enter the path to where backups should be stored. Must be absolute (eg, C:/Users/YOURNAME/Desktop)")
                        print("Enter 'internal' to store backups in the pyhoster directory\n(which always works, but almost defeats the purpose of why I made a backup system)")
                        path = input("Enter the path to where backups should be stored: ")
                        if path == "internal":
                            os.makedirs("backups", exist_ok=True)
                            path = os.path.abspath("backups/")
                        assert os.path.isabs(path)
                    except AssertionError:
                        print("Path must be absolute (eg, C:/Users/YOURNAME/Desktop). Try again.")
                        continue
                    break
            jmod.setvalue(
                key="backups_path",
                json_dir=self.settings_dir,
                value=path,
                dt=app_settings
            )
            if is_interface:
                print(f"Set backups path to \"{path}\"")
            pylogger.info(f"Set backups path to \"{path}\"")

        def api_enabled(self, enabled=None, is_interface=False):
            if is_interface or enabled==None:
                while True:
                    try:
                        answer = input("Should we enable the API Autoboot? y/n : ").lower()
                        assert answer == "y" or answer == "n"
                    except:
                        print("Invalid choice. 'y' or 'n' only")

                    enabled = True if answer == "y" else False
                    break
            
            jmod.setvalue(
                key="api.autoboot",
                json_dir=self.settings_dir,
                value=enabled,
                dt=app_settings
            )
            print("Turned off the API Autoboot." if enabled == False else "Turned on the API Autoboot.")
            pylogger.info("Turned off the API Autoboot." if enabled == False else "Turned on the API Autoboot.")
