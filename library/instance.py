import os, shutil, logging, sys, datetime, http.server, socketserver, json, threading
from .application import application as app
from .jmod import jmod
from .data_tables import config_dt

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
                boundpath: str = str(input("What is the full path to the app's content? TEXT (blank for no external binding) : "))
                if str(boundpath).lower() == "cancel":
                    print("Cancelled!")
                    return True
                if boundpath != "":
                    assert os.path.exists(boundpath) and os.path.isabs(boundpath), "The path must exist and be absolute! (absolute: starting from root directory such as C:/)"
                else:
                    boundpath = f"instances/{app_name}/"
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

        # Sets the absolute path/boundpath in the json file
        jmod.setvalue(
            "boundpath",
            f"instances/{app_name}/config.json",
            value=boundpath,
            dt=config_dt(app_name)
            )
        # Sets description
        jmod.setvalue(
            "description",
            f"instances/{app_name}/config.json",
            value=app_desc,
            dt=config_dt(app_name)
            )
        # Sets the port
        jmod.setvalue(
            "port",
            f"instances/{app_name}/config.json",
            value=port,
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
        
        # REMAINS LIKE THIS UNTIL I FIGURE OUT SUPRESSIONS
        # # Gets if the user wants it silent or not
        # try:
        #     inp = input(f"Would you like to start \"{app_name}\" silently? Y/N\n>>> ")
        #     if inp == "cancel":
        #         print("Cancelled startup")
        #         return True
        #     else:
        #         if "y" in inp.lower():
        #             is_silent = True
        #         elif "n" in inp.lower():
        #             is_silent = False
        #         else:
        #             is_silent = True # Assumes true if invalid input
        #             
        # except AssertionError as err:
        #     print(str(err))
        #     return
        
        # Ensures no other apps are running on the same port by using requests
        for app in os.listdir("instances/"):
            config_file = f"instances/{app}/config.json"
            if jmod.getvalue(key=f"autostart", json_dir=config_file) == True:
                port = jmod.getvalue(key='port', json_dir=config_file)
                if port == jmod.getvalue(key='port', json_dir=f"instances/{app_name}/config.json"):
                    if jmod.getvalue(key="running", json_dir=config_file) == True:
                        print(f"Port {port} is already in use by project {app}! Please change the port of one of the projects to add to autostart.")
                        return True

        # Starts the app
        threading.Thread(target=instance.start, args=(app_name, False)).start()

    def start(app_name, silent=False): # Silent = True makes it buggy as fuck because of how I suppressed prints. whoops 
        # Define the base directory for instances
        base_directory = os.path.abspath("instances/")

        # Construct the directory path for the specific app
        directory = os.path.join(base_directory, app_name)
        os.makedirs(directory, exist_ok=True)  # Create the directory if it doesn't exist

        # Get the port from the config.json file
        config_path = os.path.abspath(f"instances/{app_name}/config.json")
        with open(config_path, 'r') as config_file:
            config_data = json.load(config_file)
        port = config_data.get("port")

        if port is None:
            print(f"Port is not defined in config.json for {app_name}!")
            return False

        # Define a custom request handler with logging
        class CustomHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                self.content_directory = os.path.abspath(f"{base_directory}/{app_name}/content/")
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
            log_file_path = os.path.abspath(f"logs/{current_date}.log")

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
                    print(f"Server \"{app_name}\" is running. Check the logs for actions.\n"
                        f"You can visit it on http://localhost:{port}")

                log_message(f"Server \"{app_name}\" is running.")
                # Sets server to running in Json file.
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
            print(f"Server \"{app_name}\" failed to start: {e}")
            log_message(f"Server \"{app_name}\" failed to start: {e}")

    def close(app_name):
        pass