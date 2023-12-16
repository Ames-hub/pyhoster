import logging, os, multiprocessing as mp, json, time
from .data_tables import app_settings, web_config_dt, wsgi_config_dt
from .filetransfer import ftp
from .warden import warden
from .jmod import jmod
from .userman import userman
from .API.Controller import controller as apicontroller
from .WebGUI.webgui import webcontroller

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
    "reset": "\033[0m"
}

def getkwrd(keywords, text, default=None):
    try:
        text = str(text).lower()
        keywords = [str(keyword).lower() for keyword in keywords]
    except ValueError as err:
        logging.error(f"Error: Kward bad type. Error: {err}")

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

class application:

    def run(keybind_listen: bool = True):
        application.running = True
        if FTP_Enabled == True:
            time.sleep(1) # Give the FTP server time to start up

        def help_msg():
            print("Available Commands:")
            if bool(os.environ.get("PYHOST_KEYBIND_LISTEN",True)) == False:
                print("NONE: Input has been disabled. How did you even get here?")
            else:
                print("Note: *<arg> = Required information, <arg> = Optional information")
                print("do <arg_name>:'' = Keyword information. eg, port:'80'")
                print("edit: Edits an app")
                print("start: Starts an app")
                print("restart: Turns off then on an app")
                print("stop: Stops an app")
                print("update: Updates an app")
                print("rollback: Rollback to latest backup of an app or an earlier snapshot!")
                print("help: Displays this message")
                print("cls: Clears the screen\n")
                print("enter: Enters an app's GUI")
                print("ftp: Enters the FTP GUI")
                print("warden: Enters the Warden GUI")
                print("userman: Enters the User Management GUI")
                print("api: Enters the API GUI")
                print("gui: Opens the web GUI")
                print("webgui: Enters the web GUI")
                print("pyhost: Opens the settings menu\n")
                print("create: Creates a new app")

                print("webcreate: Creates a new website app")
                print("`webcreate *<app_name> port:'80' desc:'a cool app' autostart:'True|False' boundpath:'C:/users/ME/desktop/myCoolWebsitesContent/'`")
                print("wsgicreate: Creates a new WSGI app")
                print("`wsgicreate *<app_name> port:'80' desc:'a cool app' autostart:'True|False' boundpath:'C:/users/ME/desktop/cool_app.py'`")

                print("delete: Deletes an app")
                print("`delete *<app_name>`\n")

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
                    logging.info("New command entered! Debug Info:")
                    logging.info(f"Command: {cmd} | Text: {text} | Has Args: {has_args}")
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
                        print(colours["orange"]+"Note: WSGI server's are currently in open alpha and may not work as expected."+colours["reset"])
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
                    elif cmd == "cls":
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
            # os.system('cls' if os.name == "nt" else "clear")
            print("...\nExit signal received: Program is now exiting.")
            logging.info("Exit signal received: Program is now exiting.")
            print("Shutting down logging system...")
            logging.shutdown()

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
                logging.error(f"Error stopping thread: {err}")
            print("All web instances have been shut down.")

            try:
                active_threads = mp.active_children()
                for thread in active_threads:
                    os.kill(thread.pid, 2)
                print("All threads have been gracefully shut down. (1)")
            except PermissionError:
                try:
                    active_threads = mp.active_children() # Gets all active threads again as some may have been shut down
                    for thread in active_threads:
                        os.kill(thread.pid, 9)
                        print("All threads have been shut down. (2)")
                except PermissionError:
                    try:
                        active_threads = mp.active_children()
                        for thread in active_threads:
                            thread.terminate()
                        print("All threads have been shut down. (3)")
                    except PermissionError:
                        print("Permission Error: Unable to shutdown all threads!")

            # Sets all the JSON file's running key to False
            from .jmod import jmod

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
            tokenManPid = jmod.getvalue(
                key="api.tokenManPid",
                json_dir="settings.json",
                dt=app_settings,
                default=None
            ) 
            if tokenManPid != None:
                try:
                    os.kill(tokenManPid, 2)
                except:
                    try:
                        os.kill(tokenManPid, 9)
                    except:
                        pass

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
                    logging.info("Failed to kill API process. It may have already been killed.")
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

            print("Exiting...")
            exit()

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
            while True:
                try:
                    port: int = input("What port should the app run on? NUMBER (Default: 80) : ")
                    if str(port).lower() == "cancel":
                        print("Cancelled!")
                        return True
                    if str(port) == "":
                        port = 80
                    assert type(int(port)) is int, "The port must be an integer!"
                    port = int(port)
                    assert port > 0 and port < 65535, "The port must be between 0 and 65535!"
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
            
            logging.info("Turned off autostarts." if state == False else "Turned on Autostarts.")

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
            
            logging.info("Turned off the 404 Page." if state == False else "Turned on the 404 Page.")
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
            logging.info(f"Set backups path to \"{path}\"")

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
            logging.info("Turned off the API Autoboot." if enabled == False else "Turned on the API Autoboot.")