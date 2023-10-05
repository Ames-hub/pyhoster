import os, shutil, logging, sys, datetime, http.server, socketserver, json
from .application import application as app
from .jmod import jmod
from .data_tables import config_dt
import multiprocessing as threading

root_dir = os.getcwd()

class instance: # Do not use apptype in calls until other apptypes are made
    def create(do_autostart: bool = False, apptype: app.types.webpage = app.types.webpage):
        # Gets input if not provided
        input() # This input statement catches the 'create' text entered to call this def. Its purely aesthetic, not functional.
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
        
        # Gets the app description
        while True:
            try:
                print("\nInstructions: <nl> = new line")
                app_desc: str = str(input("What is the app's description? TEXT (optional) : "))
                if app_desc.lower() == "cancel":
                    print("Cancelled!")
                    return True
                assert type(app_desc) == str, "The description must be a string!"
                if app_desc == "":
                    app_desc = "A Website hosted by Pyhost."
                app_desc.replace("<nl>", "\n") # Replaces <nl> with a new line
                break
            except AssertionError as err: # Forces the description to be valid
                print(str(err))
                continue

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

        while True:
            try:
                print("\nThis directory will be copied to the app's content folder. You work on the project in this directory.")
                print("Internal binding will be: "+str(os.path.abspath(f"instances/{app_name}/content/")))
                boundpath: str = str(input("What is the full path to the app's content? TEXT (blank for no external binding) : "))
                if str(boundpath).lower() == "cancel":
                    print("Cancelled!")
                    return True
                if boundpath != "":
                    assert os.path.exists(boundpath) and os.path.isabs(boundpath), "The path must exist and be absolute! (absolute: starting from root directory such as C:/)"
                else:
                    boundpath = str(os.path.abspath(f"instances/{app_name}/content/"))
                break
            except AssertionError as err: # Forces the path to be valid and absolute
                print(str(err))
                continue
        
        while True:
            try:
                do_autostart: str = input("Should the app autostart? Y/N : ").lower()
                if do_autostart == "cancel":
                    print("Cancelled!")
                    return True
                if "y" in do_autostart:
                    do_autostart = True
                elif "n" in do_autostart:
                    do_autostart = False
                else:
                    raise AssertionError("The autostart must be either 'Y' or 'N'!")
                assert type(do_autostart) is bool, "The autostart must be a boolean!"
                break
            except AssertionError as err: # Forces the autostart to be valid
                print(str(err))
                continue

        # Makes the appropriate directories
        os.makedirs(f"instances/{app_name}/", exist_ok=True)
        os.makedirs(f"instances/{app_name}/content/", exist_ok=True)
        # Copies all the content from the absolute path to the app's content folder using shutil
        if boundpath != f"instances/{app_name}/":
            shutil.copytree(boundpath, f"instances/{app_name}/content/", dirs_exist_ok=True)

        from .autostart import autostart
        # Sets the autostart and creates config.json if applicable
        if do_autostart == True:
            autostart.add(app_name)

        config_path = f"instances/{app_name}/config.json"
        # Sets the absolute path/boundpath in the json file
        jmod.setvalue(
            "boundpath",
            config_path,
            value=boundpath,
            dt=config_dt(app_name)
            )
        # Sets description
        jmod.setvalue(
            "description",
            config_path,
            value=app_desc,
            dt=config_dt(app_name)
            )
        # Sets the port
        jmod.setvalue(
            "port",
            config_path,
            value=port,
            dt=config_dt(app_name)
        )
        # Sets the content directory
        jmod.setvalue(
            "contentloc",
            config_path,
            value=os.path.abspath(f"instances/{app_name}/content/"),
            dt=config_dt(app_name)
        )

        os.system('cls' if os.name == "nt" else "clear")
        # Prints with green
        print("\033[92m" + f"Created app \"{app_name}\" successfully!" + "\033[0m")
        logging.info(f"Created app \"{app_name}\" successfully!")

    def delete():
        input() # This input statement catches the 'delete' text entered to call this def. Its purely aesthetic, not functional.
        try: # Asks for the app name
            os.system('cls' if os.name == "nt" else "clear")
            print("\nWARNING: "+"\033[91m"+"YOU ARE ABOUT TO DELETE AN APP\n"+"\033[0m"+"All app names below...\n")
            for app in os.listdir("instances/"):
                print(app)
                # Prints description in gray then resets to white
                print("\033[90m"+jmod.getvalue(key="description", json_dir=f"instances/{app}/config.json")+"\033[0m")
            else:
                print("\nType Cancel to cancel deletion.")
            app_name: str = str(input("What is the name of the app? TEXT : "))
            if app_name.lower() == "cancel":
                print("Cancelled!")
                return True
            assert app_name in os.listdir("instances/"), "The app must exist!"
        except AssertionError as err:
            print(str(err))

        try:
            inp = input(f"Are you sure you want to delete \"{app_name}?\" Press enter to confirm. Otherwise, type cancel then enter to cancel.\n>>> ")
            if inp != "":
                raise AssertionError("Cancelled!")
        except AssertionError as err:
            print(str(err))
            return
        
        # Deletes the app's folder
        shutil.rmtree(f"instances/{app_name}/")

        # Prints in green
        print("\033[92m" + f"Deleted app \"{app_name}\" successfully!" + "\033[0m")
        logging.info(f"Deleted app \"{app_name}\" successfully!")

    def start_interface():
        '''a def for the user to start an app from the command line easily via getting the app name from the user'''
        input() # Aesthetic input statement to catch the 'start' text entered to call this def
        
        # Prints all app names, then asks for the app name they want to start
        os.system('cls' if os.name == "nt" else "clear")
        print("\nAll app names below...\nDescriptions are in "+"\033[90m"+"gray"+"\033[0m \n")
        for app in os.listdir("instances/"):
            print(app)
            # Prints description in gray then resets to white
            print("\033[90m"+jmod.getvalue(key="description", json_dir=f"instances/{app}/config.json")+"\033[0m")
        else:
            print("\nType Cancel to cancel initialization.")
        
        try:
            app_name: str = str(input("What is the name of the app? TEXT : "))
            if app_name.lower() == "cancel":
                print("Cancelled!")
                return True
            assert app_name in os.listdir("instances/"), "The app must exist!"
        except AssertionError as err:
            print(str(err))
            return
        
        # Ensures no other apps are running on the same port by using requests
        for app in os.listdir("instances/"):
            config_file = f"instances/{app}/config.json"
            if jmod.getvalue(key=f"autostart", json_dir=config_file) == True:
                port = jmod.getvalue(key='port', json_dir=config_file)
                if port == jmod.getvalue(key='port', json_dir=f"instances/{app_name}/config.json"):
                    if jmod.getvalue(key="running", json_dir=config_file) == True:
                        if app != app_name:
                            print(f"Port {port} is already in use by project {app}! Please change the port of one of the other projects or stop a one.")
                            return True
                        else:
                            print(f"That app is already running! To stop it, use the stop command.")
                            return True
        
        website = threading.Process(
            target=instance.start, args=(app, False),
            name=f"{app_name}_webserver"
            )
        website.start()
        pid = website.pid
        jmod.setvalue(
            key="pid",
            json_dir=f"instances/{app_name}/config.json",
            value=pid,
            dt=config_dt(app_name)
        )

    def start(app_name, silent=False): # Silent = True makes it buggy as fuck because of how I suppressed prints. whoops 
        # Define the base directory for instances
        base_directory = os.path.abspath("instances/")

        # Construct the directory path for the specific app
        directory = os.path.join(base_directory, app_name)
        os.makedirs(directory, exist_ok=True)  # Create the directory if it doesn't exist

        # Get the port from the config.json file
        config_path = os.path.abspath(f"instances/{app_name}/config.json")
        with open(config_path, 'r') as config_file:
            config_data: dict = json.load(config_file)
        port = config_data.get("port")

        if port is None:
            print(f"Port is not defined in config.json for {app_name}!")
            return False

        # Define a custom request handler with logging
        class CustomHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                self.content_directory = config_data.get("contentloc")
                super().__init__(*args, directory=self.content_directory, **kwargs)

            def do_GET(self):
                self.log_request_action()
                # Check if the content directory is empty
                if not os.listdir(self.content_directory):
                    self.serve_default_html()
                else:
                    super().do_GET()

            def serve_default_html(self):
                default_html_path = os.path.abspath(f"{root_dir}/library/default.html")
                with open(default_html_path, 'rb') as default_html_file:
                    content = default_html_file.read()
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(content)

            def log_request_action(self):
                client_address = self.client_address[0]
                requested_file = self.path
                current_date = datetime.date.today().strftime("%Y-%m-%d")
                log_file_path = f"{base_directory}/{app_name}/logs/{current_date}.log"

                with open(log_file_path, "a") as log_file:
                    if requested_file == "/":
                        log_file.write(f"{datetime.datetime.now()} - {app_name} - IP {client_address} requested the landing page\n")
                    else:
                        log_file.write(f"{datetime.datetime.now()} - {app_name} - IP {client_address} requested file {requested_file}\n")

        # Define a custom log message function
        def log_message(message):
            current_date = datetime.date.today().strftime("%Y-%m-%d")
            log_file_path = os.path.abspath(f"instances/{app_name}/logs/{current_date}.log")

            with open(log_file_path, "a") as log_file:
                log_file.write(f"{datetime.datetime.now()} - {app_name} - {message}\n")

        # Create the log directory if it doesn't exist
        log_directory = f"{base_directory}/{app_name}/logs/"
        os.makedirs(log_directory, exist_ok=True)

        # Redirect stdout and stderr to /dev/null if silent is True
        if silent:
            sys.stdout = open(os.devnull, "w")
            sys.stderr = open(os.devnull, "w")

        try:
            # Create a socket server with the custom handler
            with socketserver.TCPServer(("", port), CustomHandler) as httpd:
                # Print a message to indicate the server has started unless silent is True
                if not silent:
                    print(f"Server \"{app_name}\" is running on port {port}. Check the logs for actions.\n"
                        f"You can visit it on http://localhost:{port}")

                log_message(f"Server \"{app_name}\" is running.")
                # Get the PID of the current thread (web server)

                # Sets server to running in JSON file and save the PID
                jmod.setvalue(
                    key="running",
                    json_dir=f"instances/{app_name}/config.json",
                    value=True,
                    dt=config_dt(app_name)
                )

                # Start the server and keep it running until interrupted
                logging.info(f"Server \"{app_name}\" is now running on port {port}")
                httpd.serve_forever()

        except OSError as e:
            if not silent:
                print(f"Server \"{app_name}\" failed to start: {e}")
            log_message(f"Server \"{app_name}\" failed to start: {e}")

    def stop_interface():
        '''a def for the user to stop an app from the command line easily via getting the app name from the user'''
        input()

        # Prints all app names, then asks for the app name they want to stop
        os.system('cls' if os.name == "nt" else "clear")
        print("\nAll app names below...\nDescriptions are in "+"\033[90m"+"gray"+"\033[0m \n")
        for app in os.listdir("instances/"):
            # Ensures app is running
            if jmod.getvalue(key="running", json_dir=f"instances/{app}/config.json") == True:
                print(app)
                # Prints description in gray then resets to white
                print("\033[90m"+str(jmod.getvalue(key="description", json_dir=f"instances/{app}/config.json")).replace("<nl>","\n")+"\033[0m")
        else:
            print("\nType Cancel to cancel stopping an app.")
            while True: # Retry logic
                try:
                    app_name = input(">>> ")
                    if app_name.lower() == "cancel":
                        print("Cancelled!")
                        return True
                    assert app_name in os.listdir("instances/"), "The app must exist!"
                    break
                except AssertionError as err:
                    print(str(err))
                    continue

        # Stops the app
        instance.stop(app_name)

    def stop(app_name):
        try:
            # Get the process ID (PID) of the running web server for the specified app
            config_path = os.path.abspath(f"instances/{app_name}/config.json")
            with open(config_path, 'r') as config_file:
                config_data = json.load(config_file)
            pid = config_data.get("pid")

            if pid is None:
                print(f"PID is not defined in config.json for {app_name}!")
                return False

            # Terminate the web server process gracefully.
            try:
                os.kill(pid, 2)
            except PermissionError:
                try:
                    os.kill(pid, 9) # Try by force, if 2 wont work.
                except:
                    print("I don't have permission to do that! Try again later.")
            # signal 2 = CTRL + C
            # This works because the process its interrupting is actually a python script
            # And this causes a keyboardinterrupt exception, which causes it to stop.

            # Update the JSON file to indicate that the server is not running
            jmod.setvalue(
                key="running",
                json_dir=f"instances/{app_name}/config.json",
                value=False,
                dt=config_dt(app_name)
            )

            print(f"Server \"{app_name}\" has been stopped.")
            logging.info(f"Server \"{app_name}\" has been stopped.")

        except Exception as e:
            print(f"Failed to stop server \"{app_name}\": {e}")
            logging.error(f"Failed to stop server \"{app_name}\": {e}")

    class edit():
        def __init__(self, app_name=None, is_interface=True) -> None:
            if is_interface:
                input() # Catches the edit command
                while True: # Retry logic
                    try:
                        print("\nAll app names below...\nDescriptions are in "+"\033[90m"+"gray"+"\033[0m \n")
                        for app in os.listdir("instances/"):
                            print(app)
                            # Prints description in gray then resets to white
                            print("\033[90m"+jmod.getvalue(key="description", json_dir=f"instances/{app}/config.json")+"\033[0m")
                        else:
                            print("\nType Cancel to cancel editing.")
                        app_name: str = str(input("What is the name of the app? TEXT : "))
                        if app_name.lower() == "cancel":
                            print("Cancelled!")
                            return True
                        assert app_name in os.listdir("instances/"), "The app must exist!"
                        break
                    except:
                        pass

            # Ensure an app_name can be gotten
            try:
                if not is_interface:
                        assert app_name is not None, "App name is not defined!"
                elif app_name is None:
                    assert is_interface == True
            except:
                print("App name is not defined!")
                return

            self.app_name = app_name
            self.config_dir = os.path.abspath(f"instances/{app_name}/config.json")
            with open (self.config_dir, "r") as config_file:
                self.config_data = json.load(config_file)

            # Stops the server if its not already stopped
            print("Stopping selected server for stability purposes.")
            instance.stop(self.app_name)

            self.take_command()

        def take_command(self):
            '''The def that handles input from the user on how to edit the app.'''
            print("What would you like to edit about the app?")
            print("1. Name")
            print("2. Port")
            print("3. Description")
            print("4. Bound Path")
            print("5. Autostart")
            print("6. Cancel\n")
            while True:
                try:
                    option = input(">>> ")
                    if option.isnumeric() == True:
                        choice_dict = {
                            1: "name",
                            2: "port",
                            3: "description",
                            4: "boundpath",
                            5: "autostart",
                            6: "stop edit"
                        }
                        option = choice_dict[int(option)]
                        
                        if "stop" in option:
                            self.end_edit()
                    else:
                        option = option.lower()
                        
                        if "stop" in option:
                            self.end_edit()
                        elif "name" in option:
                            self.name()
                        elif "port" in option:
                            self.port()
                        elif "description" in option:
                            self.description()
                        elif "boundpath" in option:
                            self.boundpath()
                        elif "autostart" in option:
                            self.autostart()
                        elif "cancel" in option:
                            self.end_edit()
                        else:
                            raise KeyError

                except AssertionError as err:
                    print(str(err))
                    continue
                except KeyError:
                    print("Invalid option!")
                    continue

        def end_edit(self):
            '''Ends the edit process'''
            print("Stoping edit...")
            startup = input("Would you like to start the app up? Y/N : ").lower()
            if "y" in startup:
                instance.start(self.app_name, True)
                print("App started.")
            return True

        def name(self, new_name=None):
            '''edits an apps name'''
            # Stops the server if its not already stopped
            instance.stop(self.app_name)

            # Gets new name input if not provided
            if new_name == None:
                new_name = input("What is the new name of the app? TEXT : ")
                if new_name.lower() == "cancel":
                    print("Cancelled!")
                    return True
                
                # Makes sure the app name is valid and can be made into a directory folder
                assert not new_name.startswith(" "), "The name cannot start with a space!"
                assert not new_name.endswith(" "), "The name cannot end with a space!"
                assert "." not in new_name, "The name cannot have a period!"
                assert "/" not in new_name and "\\" not in new_name, "The name cannot contain a slash!"
                assert "_" not in new_name, "The name cannot contain an underscore!"
                assert "-" not in new_name, "The name cannot contain a dash!"
                assert ":" not in new_name, "The name cannot contain a colon!"
                assert new_name != "", "The name cannot be blank!"

                # Renames folder, and updates the self variable
                old_dir = os.path.abspath(f"instances/{self.app_name}/")
                new_dir = os.path.abspath(f"instances/{new_name}/")
                os.rename(old_dir, new_dir)

                self.app_name = new_name
                self.config_dir = os.path.abspath(f"instances/{new_name}/config.json")
                with open (self.config_dir, "r") as config_file:
                    self.config_data = json.load(config_file)

                # Updates the json file with the new name
                jmod.setvalue(
                    key="name",
                    json_dir=self.config_dir,
                    value=new_name,
                    dt=config_dt(new_name)
                )
                print(f"Changed name to {new_name} successfully!")

        def port(self, new_port=None):
            '''edits an apps port'''
            # Stops the server if its not already stopped
            instance.stop(self.app_name)

            # Gets new port input if not provided
            if new_port == None:
                while True:
                    try:
                        new_port = input("What is the new port of the app? NUMBER : ")
                        if new_port.lower() == "cancel":
                            print("Cancelled!")
                            return True
                        assert type(int(new_port)) is int, "The port must be an integer!"
                        new_port = int(new_port)
                        assert new_port > 0 and new_port < 65535, "The port must be between 0 and 65535!"
                        break
                    except (AssertionError, ValueError) as err:
                        print(str(err))
                        continue

            # Updates the json file with the new port
            jmod.setvalue(
                key="port",
                json_dir=self.config_dir,
                value=new_port,
                dt=config_dt(self.app_name)
            )
            print(f"Changed port to {new_port} successfully!")

        def description(self, new_desc=None):
            '''edits an apps description'''
            # Stops the server if its not already stopped
            instance.stop(self.app_name)

            # Gets new description input if not provided
            if new_desc == None:
                print("\nInstructions: <nl> = new line")
                new_desc = input("What is the new description of the app? TEXT (optional) : ")
                if new_desc.lower() == "cancel":
                    print("Cancelled!")
                    return True
                assert type(new_desc) == str, "The description must be a string!"
                if new_desc == "":
                    new_desc = "A Website hosted by Pyhost."
                new_desc.replace("<nl>", "\n") # Replaces <nl> with a new line

            # Updates the json file with the new description
            jmod.setvalue(
                key="description",
                json_dir=self.config_dir,
                value=new_desc,
                dt=config_dt(self.app_name)
            )
            print(f"Changed description to\n\"{new_desc}\"\nsuccessfully!")

        def boundpath(self, new_boundpath=None):
            '''edits an apps boundpath'''
            # Stops the server if its not already stopped
            instance.stop(self.app_name)

            # Gets new boundpath input if not provided
            if new_boundpath == None:
                abs_content_dir = str(os.path.abspath(f"instances/{self.app_name}/content/"))
                while True:
                    try:
                        print("\nThis directory will be copied to the app's content folder. You work on the project in this directory.")
                        print("Internal binding will be: "+abs_content_dir)
                        new_boundpath = input("What is the new full path to the app's content? TEXT (blank for no external binding) : ")
                        if new_boundpath.lower() == "cancel":
                            print("Cancelled!")
                            return True
                        if new_boundpath != "":
                            assert os.path.exists(new_boundpath) and os.path.isabs(new_boundpath), "The path must exist and be absolute! (absolute: starting from root directory such as C:/)"
                        else:
                            new_boundpath = abs_content_dir
                        break
                    except AssertionError as err:
                        print(str(err))
                        continue

            # Copies all the content from the absolute path to the app's content folder using shutil
            if new_boundpath != abs_content_dir:
                shutil.copytree(new_boundpath, abs_content_dir, dirs_exist_ok=True)

            # Updates the json file with the new boundpath
            jmod.setvalue(
                key="boundpath",
                json_dir=self.config_dir,
                value=new_boundpath,
                dt=config_dt(self.app_name)
            )
            print(f"Changed externally boundpath to {new_boundpath} successfully!")

        def autostart(self, is_autostart=None):
            '''edits an apps autostart'''
            # Stops the server if its not already stopped
            instance.stop(self.app_name)

            # Gets new autostart input if not provided
            if is_autostart == None:
                while True:
                    try:
                        is_autostart = input("Should the app autostart? Y/N : ").lower()
                        from .autostart import autostart
                        
                        if is_autostart == "cancel":
                            print("Cancelled!")
                            return True
                        if "y" in is_autostart:
                            autostart.add(self.app_name)
                            print("Added to autostart successfully!")
                        elif "n" in is_autostart:
                            autostart.remove(self.app_name)
                            print("Removed from autostart successfully!")
                        else:
                            raise AssertionError("The autostart must be either 'Y' or 'N'!")
                        assert type(is_autostart) is bool, "The autostart must be a boolean!"
                        break
                    except AssertionError as err:
                        print(str(err))
                        continue
