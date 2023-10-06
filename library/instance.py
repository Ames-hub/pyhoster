import os, shutil, logging, sys, datetime, http.server, socketserver, json, hashlib, random
from .application import application as app
from .jmod import jmod
from .data_tables import config_dt, app_settings
import multiprocessing as threading


root_dir = os.getcwd()
setting_dir = os.path.join(root_dir, "settings.json")

class instance: # Do not use apptype in calls until other apptypes are made
    def create(app_name:str=None, app_desc:str=None, port:int=None, boundpath:str=None,
               do_autostart: bool = False, apptype: app.types.webpage = app.types.webpage):
        '''All needed args that are not provided will be grabbed from the user'''
        
        try:
            if app_name != None:
                app_name = str(app_name)
            if app_desc != None:
                app_desc = str(app_desc)
            if port != None:
                port = int(port)
            if boundpath != None:
                boundpath = str(boundpath)
                if os.path.isabs(boundpath) == False:
                    raise TypeError("Boundpath must be absolute!")
            if do_autostart != None:
                do_autostart = bool(do_autostart)
        except TypeError as err:
            print("Invalid argument Types! : "+str(err))
        
        if app_name != None:
            try:
                # Makes sure the app name is valid and can be made into a directory folder
                assert not app_name.startswith(" "), "The name cannot start with a space!"
                assert not app_name.endswith(" "), "The name cannot end with a space!"
                assert "." not in app_name, "The name cannot have a period!"
                assert "/" not in app_name and "\\" not in app_name, "The name cannot contain a slash!"
                assert "_" not in app_name, "The name cannot contain an underscore!"
                assert "-" not in app_name, "The name cannot contain a dash!"
                assert ":" not in app_name, "The name cannot contain a colon!"
                assert app_name != "", "The name cannot be blank!"
            except AssertionError:
                print("The name must be a valid name! (Must be able to be put in a file's name)")
                app_name = None
        
        # Gets input if not provided. Do not use Elif, so that if it failed assertion before it'll fix here
        if app_name == None:
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
        if app_desc == None:
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

        # Gets the port
        if port == None:
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

        # Gets external bound directory
        if boundpath == None:
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
        
        # asks if the app should autostart
        if do_autostart == None:
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
        config = config_dt
        jmod.setvalue(
            "name",
            config_path,
            value=app_name,
            dt=config
            )
        jmod.setvalue(
            "boundpath",
            config_path,
            value=boundpath,
            dt=config
            )
        # Sets description
        jmod.setvalue(
            "description",
            config_path,
            value=app_desc,
            dt=config
            )
        # Sets the port
        jmod.setvalue(
            "port",
            config_path,
            value=port,
            dt=config
        )
        # Sets the content directory
        jmod.setvalue(
            "contentloc",
            config_path,
            value=os.path.abspath(f"instances/{app_name}/content/"),
            dt=config
        )

        os.system('cls' if os.name == "nt" else "clear")
        # Prints with green
        print("\033[92m" + f"Created app \"{app_name}\" successfully!" + "\033[0m")
        logging.info(f"Created app \"{app_name}\" successfully!")

    def delete(app_name:str=None, is_interface:bool=False, ask_confirmation:bool=True):
        
        if is_interface == True or app_name == None:
            try: # Asks for the app name
                os.system('cls' if os.name == "nt" else "clear")
                print("\nWARNING: "+"\033[91m"+"YOU ARE ABOUT TO DELETE AN APP\n"+"\033[0m"+"All app names below...\n")
                for app in os.listdir("instances/"):
                    print(app)
                    # Prints description in gray then resets to white
                    print("\033[90m"+str(jmod.getvalue(key="description", json_dir=f"instances/{app}/config.json")).replace("<nl>","\n")+"\033[0m")
                else:
                    print("\nType Cancel to cancel deletion.")
                app_name: str = str(input("What is the name of the app? TEXT : "))
                if app_name.lower() == "cancel":
                    print("Cancelled!")
                    return True
                assert app_name in os.listdir("instances/"), "The app must exist!"
            except AssertionError as err:
                print(str(err))

        if ask_confirmation:
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

    def start_interface(app_name=None, is_interface=True):
        '''a def for the user to start an app from the command line easily via getting the app name from the user'''
        
        if is_interface == True and app_name == None:
            # Prints all app names, then asks for the app name they want to start
            os.system('cls' if os.name == "nt" else "clear")
            print("\nAll app names below...\nDescriptions are in "+"\033[90m"+"gray"+"\033[0m \n")
            for app in os.listdir("instances/"):
                if jmod.getvalue(key="running", json_dir=f"instances/{app}/config.json") == False:
                    print(app) # Only prints apps that havent been started yet
                    # Prints description in gray then resets to white
                    print("\033[90m"+str(jmod.getvalue(key="description", json_dir=f"instances/{app}/config.json")).replace("<nl>","\n")+"\033[0m")
            else:
                print("\nType Cancel to cancel initialization.")
            
            try:
                app_name: str = str(input("What is the name of the app? TEXT : "))
                if app_name.lower() == "cancel":
                    print("Cancelled!")
                    return True
                assert app_name in os.listdir(os.path.abspath("instances/")), "The app must exist!"
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
            target=instance.start, args=(app_name, True),
            name=f"{app_name}_webserver"
            )
        website.start()
        pid = website.pid
        jmod.setvalue(
            key="pid",
            json_dir=f"instances/{app_name}/config.json",
            value=pid,
            dt=config_dt
        )

    def start(app_name, silent=True): # Silent = True makes it buggy as fuck because of how I suppressed prints. whoops 
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

        # Loads settings
        send_404 = jmod.getvalue( # If this setting is updated, the app needs to restart
            key="send_404_page",
            json_dir=setting_dir,
            default=True,
            dt=app_settings
            )
        default_index = jmod.getvalue(
            key="index",
            json_dir=config_path,
            default="index.html",
            dt=config_data
            )
        

        # Define a custom request handler with logging
        class CustomHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                self.content_directory = config_data.get("contentloc")
                super().__init__(*args, directory=self.content_directory, **kwargs)
            
            def do_GET(self):
                self.log_request_action()
                if self.path == "/":
                    # Serve the default_index as the landing page
                    default_index_path = os.path.abspath(os.path.join(self.content_directory, default_index))
                    if os.path.exists(default_index_path):
                        with open(default_index_path, 'rb') as index_file:
                            content = index_file.read()
                            self.send_response(200)
                            self.send_header("Content-type", "text/html")
                            self.end_headers()
                            self.wfile.write(content)
                    else:
                        self.serve_default_html()
                else:
                    super().do_GET()

            if send_404 == True: # Doesn't define this function if not send 404
                def serve_default_html(self):
                    default_html_path = os.path.abspath(f"{root_dir}/library/default.html")
                    with open(default_html_path, 'rb') as default_html_file:
                        content = default_html_file.read()
                        # Replace the placeholder text with the app name
                        content = content.replace(b"{{app_name}}", bytes(app_name, "utf-8"))
                        content = content.replace(b"{{content_dir}}", bytes(self.content_directory, "utf-8"))

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
                    dt=config_dt
                )

                # Start the server and keep it running until interrupted
                logging.info(f"Server \"{app_name}\" is now running on port {port}")
                httpd.serve_forever()

        except OSError as e:
            logging.error(f"Server \"{app_name}\" failed to start: {e}\n\n"+str(e.with_traceback(e.__traceback__)))
            if not silent:
                print(f"Server \"{app_name}\" failed to start: {e}\nIs there already something running on port {port}?")
            log_message(f"Server \"{app_name}\" failed to start: {e}\nIs there already something running on port {port}?")

    def restart(app_name=None, is_interface=True):
        print("\n")
        if is_interface == True or app_name == None:
            for app in os.listdir("instances/"):
                if jmod.getvalue(key="running", json_dir=f"instances/{app}/config.json") == True:
                    print(app)  # Only prints apps that are running
                    # Prints description in gray then resets to white
                    print("\033[90m" + str(jmod.getvalue(key="description", json_dir=f"instances/{app}/config.json")).replace("<nl>","\n") + "\033[0m")

            while True:
                print("\nEnter app name to restart.")
                app_name = input(">>> ")
                if app_name not in os.listdir("instances/"):
                    print("That app doesn't exist!")
                    continue
                else:
                    break
    
        instance.stop(app_name)
        threading.Process(
            target=instance.start,
            args=(app_name, True),
        ).start()
        print(f"Server {app_name} has started.")
        print("\033[92m" + f"Restarted app \"{app_name}\" successfully!" + "\033[0m")


    def stop_interface():
        '''a def for the user to stop an app from the command line easily via getting the app name from the user'''
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
            success = False
            try:
                os.kill(pid, 2)
                success = True
            except PermissionError:
                try:
                    os.kill(pid, 9) # Try by force, if 2 wont work.
                    success = True
                except PermissionError:
                    print("I don't have permission to stop this app! Please again later.")
            # signal 2 = CTRL + C | signal 9 = KILL
            # This works because the process its interrupting is actually a python script
            # And this causes a keyboardinterrupt exception, which causes it to stop.
            if success:
                # Update the JSON file to indicate that the server is not running
                jmod.setvalue(
                    key="running",
                    json_dir=f"instances/{app_name}/config.json",
                    value=False,
                    dt=config_dt
                )

                print(f"Server \"{app_name}\" has been stopped.")
                logging.info(f"Server \"{app_name}\" has been stopped.")
        except FileNotFoundError as e:
            print(f"Server \"{app_name}\" is not an existant app!")
            logging.error(f"Server \"{app_name}\" is not an existant app!")
        except Exception as e:
            print(f"Failed to stop server \"{app_name}\": {e}")
            logging.error(f"Failed to stop server \"{app_name}\": {e}")

    def update(app_name=None, is_interface=False):

        def calculate_file_hash(file_path):
            BLOCKSIZE = 65536
            hasher = hashlib.sha1()
            with open(file_path, 'rb') as file:
                buf = file.read(BLOCKSIZE)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = file.read(BLOCKSIZE)
            return hasher.hexdigest()

        if is_interface:
            while True:
                try:
                    print("\nAll app names below...\nDescriptions are in " + "\033[90m" + "gray" + "\033[0m \nName is "+"\033[91m"+"red"+"\033[0m"+" if outdated, "+"\033[96m"+"cyan"+"\033[0m"+" if up to date and finally "+"\033[93m"+"yellow"+"\033[0m"+" if the content folder is empty\n")
                    for app in os.listdir("instances/"):
                        # Get the paths for external (boundpath) and internal (content_dir) directories
                        boundpath = jmod.getvalue(key="boundpath", json_dir=f"instances/{app}/config.json")
                        content_dir = jmod.getvalue(key="contentloc", json_dir=f"instances/{app}/config.json")

                        if os.listdir(content_dir) == []: # Prints in yellow to indicate empty
                            print("\033[93m" + app + "\033[0m")
                            continue # Continue, nothing to compare.

                        # Get the file hash for each file in the external (boundpath) directory
                        ext_dirlist: list = os.listdir(boundpath)
                        ext_dirlist.sort()
                        ext_hashes = {}
                        for file in ext_dirlist:
                            ext_file_path = os.path.join(boundpath, file)
                            ext_hashes[file] = calculate_file_hash(ext_file_path)

                        # Get the file hash for each file in the internal (content_dir) directory
                        int_dirlist: list = os.listdir(content_dir)
                        int_dirlist.sort()
                        int_hashes = {}
                        for file in int_dirlist:
                            int_file_path = os.path.join(content_dir, file)
                            int_hashes[file] = calculate_file_hash(int_file_path)

                        # Check for outdated files in the internal directory
                        outdated = False
                        for file in int_dirlist:
                            if file not in ext_hashes or ext_hashes[file] != int_hashes[file]:
                                outdated = True

                        description = "\033[90m" + str(jmod.getvalue(key="description", json_dir=f"instances/{app}/config.json")).replace("<nl>","\n") + "\033[0m"
                        if outdated == False:
                            print("\033[96m" + app + "\033[0m\n"+description) # prints cyan
                        elif outdated == True:
                            print("\033[91m" + app + "\033[0m\n"+description) # Prints red
                        else:
                            print(app+"\n"+description)

                    app_name = input("\nPlease enter the app name to update. Press enter to refresh.\n>>> ")
                    if app_name == "cancel":
                        print("Cancelled!")
                        return True
                    elif app_name in os.listdir("instances/"):
                        break
                except Exception as e:
                    pass
        
        # Overwrites internal with external directory
        boundpath = jmod.getvalue(key="boundpath", json_dir=f"instances/{app_name}/config.json")
        content_dir = jmod.getvalue(key="contentloc", json_dir=f"instances/{app_name}/config.json")
        # Removes all old files
        for file in os.listdir(content_dir):
            # Removes folders and files
            shutil.rmtree(os.path.join(content_dir, file), ignore_errors=True)
            os.remove(os.path.join(content_dir, file), dir_fd=None)
        else:
            print("Update phase 1 completed.")
        # Updates all files
        shutil.copytree(src=boundpath, dst=content_dir, dirs_exist_ok=True)
        print("Phase 2 completed.\n"+"\033[92m"+"Update completed."+"\033[0m")

    class edit():
        def __init__(self, app_name=None, is_interface=True) -> bool:
            if is_interface:
                while True: # Retry logic
                    try:
                        print("\nAll app names below...\nDescriptions are in "+"\033[90m"+"gray"+"\033[0m \n")
                        for app in os.listdir("instances/"):
                            print(app)
                            # Prints description in gray then resets to white
                            print("\033[90m"+str(jmod.getvalue(key="description", json_dir=f"instances/{app}/config.json")).replace("<nl>","\n")+"\033[0m")
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

        def get_result(self):
            '''returns a dict of the result'''
            return {
                "do_restart": self.do_restart,
                "app_name": self.app_name
            }

        def take_command(self):
            '''The def that handles input from the user on how to edit the app.'''
            print("What would you like to edit about the app?")
            print("1. Name")
            print("2. Port")
            print("3. Description")
            print("4. Boundpath")
            print("5. Autostart")
            print("6. Index Page")
            print("7. Cancel\n")
            while True:
                try:
                    option = input(">>> ").lower()
                    if option.isnumeric() == True:
                        # Handles for when the user uses a number to convert from number to text
                        choice_dict = {
                            1: "name",
                            2: "port",
                            3: "description",
                            4: "boundpath",
                            5: "autostart",
                            6: "stop"
                        }
                        option = choice_dict[int(option)]
                        
                        if "stop" in option:
                            self.end_edit()
                    else:
                        option = option.lower()
                        
                        for word in option.split(" "):
                            if word in ["cancel", "stop", "exit", "quit"]:
                                self.end_edit()
                                return True
                        
                        # Handles the options for when the user does not use a number
                        if "name" in option:
                            self.name()
                            continue
                        elif "port" in option:
                            self.port()
                            continue
                        elif "desc" in option:
                            self.description()
                            continue
                        elif "boundpath" in option:
                            self.boundpath()
                            continue
                        elif "autostart" in option:
                            self.autostart()
                            continue
                        elif "index" in option:
                            self.main_index()
                            continue
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
                print(f"\"{self.app_name}\" started! (http://localhost:{self.port})\nEdit completed and saved")
                self.do_restart = True
            elif "n" in startup:
                print("Edit completed and saved")
                self.do_restart = False
            else:
                print("Invalid answer.")
                self.do_restart = False

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
                    dt=config_dt
                )
                print(f"Changed name to {new_name} successfully!")

        def port(self, new_port=None):
            '''edits an apps port'''
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
                dt=config_dt
            )
            print(f"Changed port to {new_port} successfully!")

        def description(self, new_desc=None):
            '''edits an apps description'''

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
                dt=config_dt
            )
            print(f"Changed description to\n\"{new_desc}\"\nsuccessfully!")

        def boundpath(self, new_boundpath=None):
            '''edits an apps boundpath'''

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
                dt=config_dt
            )
            print(f"Changed externally boundpath to {new_boundpath} successfully!")

        def autostart(self, is_autostart=None):
            '''edits an apps autostart'''

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
                            autostart.add(self.app_name, start_app=False)
                            print("Added to autostart successfully!")
                        elif "n" in is_autostart:
                            autostart.remove(self.app_name)
                            print("Removed from autostart successfully!")
                        else:
                            raise AssertionError("The autostart must be either 'Y' or 'N'!")
                        break
                    except AssertionError as err:
                        print(str(err))
                        continue

        def main_index(self, filename=None):
            if filename is None:
                while True:
                    try:
                        filename = input("What is the name of the index file? (Include file extension) : ")
                        assert filename != "", "The filename cannot be blank!"
                        assert "." in filename, "The filename must include a file extension!"
                        break
                    except AssertionError as err:
                        print(str(err))

            jmod.setvalue(
                key="index",
                json_dir=self.config_dir,
                value=filename,
                dt=config_dt
            )
            print("Changed index file successfully!")
