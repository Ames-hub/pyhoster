import logging, os, multiprocessing as mp, json
from .data_tables import app_settings, config_dt
from .jmod import jmod

root_dir = os.getcwd()

class application:

    def run(keybind_listen: bool = True):
        application.running = True

        def help_msg():
            print("Available Commands:")
            if bool(os.environ.get("PYHOST_KEYBIND_LISTEN",True)) == False:
                print("NONE: Input has been disabled. How did you even get here?")
            else:
                print("Note: *<arg> = Required information, <arg> = Optional information\n")
                print("create: Creates a new app")
                print("`create *<app_name> *<app_desc> <port> <boundpath> <do_autostart>`\n")

                print("delete: Deletes an app")
                print("`delete *<app_name>`\n")
                
                print("edit: Edits an app")
                print("start: Starts an app")
                print("restart: Turns off then on an app")
                print("stop: Stops an app")
                print("update: Updates an app")
                print("rollback: Rollback to latest backup of an app or an earlier snapshot!")
                print("help: Displays this message")
                print("cls: Clears the screen")

        from .instance import instance
        try:
            while True:
                if keybind_listen == True:
                    cmd: str = str(input("Enter a command: "))
                    args = cmd.split(" ")  # For commands that have arguments
                    args[0] = args[0].lower()
                    args = cmd.split(" ")  # Split the modified command again
                    cmd = args[0]
                    args.remove(cmd)
                    has_args = True if len(args) >= 1 else False
                    # Begins listening for create, delete, edit, etc commands
                    logging.info("New command entered! Debug Info:")
                    logging.info(f"Command: {cmd}")
                    logging.info(f"Args: {args}")
                    if cmd == "create":
                    # In args, find where the first and last argument with quotation marks exist
                    # And put it into 1 argument as that is the app description
                    # This allows for spaces in the app description
                        if '"' in cmd:
                            # Find the first quote, like "Hello
                            first_quote = cmd.index('"')
                            
                            # Find the last quote, like World"
                            last_quote = cmd.rindex('"')
                            
                            app_desc = cmd[first_quote + 1:last_quote]
                            args.append(app_desc)
                            
                            # Remove the part of the command that contained the app description
                            cmd = cmd.replace(f'"{app_desc}"', '')

                        if not has_args:
                            instance.create()
                        else:
                            # If 1, 2, 3 or 4 are not provided, set them to None and let create def
                            # handle them
                            try:
                                args[1] # Arg1 == Description
                            except IndexError:
                                args.append(None)

                            try:
                                args[2]
                            except IndexError:
                                args.append(None)

                            try:
                                args[3]
                                if not os.path.isabs(args[4]):
                                    print("Invalid absolute path. Try again.")
                                    return False
                            except IndexError:
                                args.append(None)
                            
                            try:
                                args[4] # 4 == do_autostart
                            except IndexError:
                                args.append(None)

                            # Makes arg 0 and 1 required
                            try:
                                str(args[0])
                                str(args[1])
                            except:
                                print("Invalid arguments. Try again.")
                                return False

                            instance.create(
                                app_name=args[0],
                                app_desc=args[1],
                                port=args[2],
                                boundpath=args[3],
                                do_autostart=args[4],
                            )
                    elif cmd == "delete":
                        if has_args == False:
                            instance.delete(is_interface=True)
                        else:
                            instance.delete(
                                app_name=args[0],
                                ask_confirmation=True,
                            )
                    elif cmd == "edit":
                        if has_args == False:
                            instance.edit()
                        else:
                            instance.edit(
                                app_name=args[0],
                                is_interface=False
                            )
                    elif cmd == "start":
                        if not has_args:
                            instance.start_interface(is_interface=True)
                        else:
                            instance.start_interface(
                                app_name=args[0],
                                is_interface=False
                            )
                            # Such a weird bug and idk what's causing it
                    elif cmd == "restart":
                        if has_args == False:
                            instance.restart(is_interface=True)
                        else:
                            instance.restart(
                                app_name=args[0],
                                is_interface=False
                            )
                    elif cmd == "stop":
                        if has_args == False:
                            instance.stop_interface()
                        else:
                            instance.stop(app_name=args[0])
                    elif cmd == "update":
                        if has_args == False:
                            instance.update(is_interface=True)
                        else:
                            instance.update(app_name=args[0], is_interface=False)
                    elif cmd == "rollback":
                        if not has_args:
                            instance.rollback(is_interface=True)
                        else:
                            try:
                                args[1]
                            except IndexError:
                                args.append(None)

                            instance.rollback(
                                app_name=args[0],
                                is_interface=False,
                                rollback_ver=args[1],
                                )
                    elif cmd == "backup":
                        if not has_args:
                            instance.backup(is_interface=True)
                        else:
                            instance.backup(app_name=args[0], is_interface=False)
                    elif cmd == "help":
                        help_msg()
                    elif cmd == "cls":
                        print("Hello, if you see this message, that means clearing the console is not supported in your terminal (such as pufferpanel terminal).")
                        os.system("cls" if os.name == "nt" else "clear")
                    elif cmd == "":
                        pass # Idk why, but it takes 1 press of enter to have the message appear. weird
                    elif cmd == "pyhost" or cmd == "settings":
                        application.settings(is_interface=True)
                        # Starts settings configuration
                    else:
                        print("Invalid command. Please try again or do `help`")
        except KeyboardInterrupt:
            application.running = False
            # os.system('cls' if os.name == "nt" else "clear")
            print("Exit signal received: Program is now exiting.")
            logging.info("Exit signal received: Program is now exiting.")
            logging.shutdown()

            print("Shutting down all web instances...")
            # Shuts down all the threads that run the webservers
            try:
                for app in os.listdir("instances/"):
                    config_path = os.path.abspath(f"instances/{app}/config.json")
                    with open(config_path, 'r') as config_file:
                        config_data = json.load(config_file)
                    pid = config_data.get("pid")

                    if pid is None:
                        print(f"PID is not defined in config.json for {app}!")
                        choice = input("Would you like to forcefully terminate? (y/n): ")
                        if choice.lower() == "y":
                            os.kill(pid, 9)
                            # signal 9 == SIGKILL
                        else:
                            print("Skipping...")
                            continue

                    # Terminate the web server process gracefully.
                    os.kill(pid, 2)
                    # signal 2 == CTRL + C
            except Exception as e:
                logging.error(f"Error stopping thread: {e}")
            print("All web instances have been shut down.")

            # Sets all the JSON file's running key to False
            from .jmod import jmod

            print("Setting all instances to not running...")
            os.makedirs("instances", exist_ok=True)
            for app in os.listdir("instances/"):
                jmod.setvalue(
                    key="running",
                    json_dir=f"instances/{app}/config.json",
                    value=False,
                    dt=config_dt
                )
            print("All instances have been set to not running.")

            # Sets all PID's to None
            print("Setting all PID's to None...")
            for app in os.listdir("instances/"):
                jmod.setvalue(
                    key="pid",
                    json_dir=f"instances/{app}/config.json",
                    value=None,
                    dt=config_dt
                )
            print("All PID's have been set to None.")

            print("Exiting...")
            exit()

    class types:
        def webpage():
            return "WEBPAGE"
    
    class settings():
        def __init__(self, is_interface=False) -> None:
            self.is_interface = is_interface
            self.settings_dir = os.path.abspath("settings.json")

            if is_interface:
                acceptable_choices = {
                    "exit": "Ends the settings edit session.",
                    "help": "Gives information on commands. Its this menu here",
                    "do autostart": "Set if we look for autostart apps on initialization. BOOL",
                    "send 404 page": "Toggle if we send the default.html aka '404' page for when an app has no index or good place to route to. BOOL",
                    "backups path": "Set the path to where backups are stored. TEXT",
                    "autobackup": "Toggle if we autobackup a snapshot of the app. BOOL",
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
                        path = input("Enter the path to where backups should be stored: ")
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