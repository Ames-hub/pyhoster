import os, shutil, logging, sys, datetime, http.server, socketserver, json, hashlib, time
from .application import application as app
from .jmod import jmod
from .data_tables import web_config_dt, wsgi_config_dt, app_settings
import multiprocessing
import waitress
import ssl

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

root_dir = os.getcwd()
setting_dir = "settings.json"

class instance: # Do not use apptype in calls until other apptypes are made
    def create_web(app_name:str=None, app_desc:str=None, port:int=None, boundpath:str=None, do_autostart: bool = False):
        '''All needed args that are not provided will be grabbed from the user'''
        try:
            if app_name != None:
                app_name = str(app_name)
            if app_desc != None:
                app_desc = str(app_desc)
            if port != None:
                port = int(port)
            if boundpath != None and boundpath != "internal":
                boundpath = str(boundpath)
                if not os.path.isabs(boundpath):
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
        while app_name == None or " " in app_name:
            app_name = app.datareqs.get_name()
            if " " in app_name:
                print("The name cannot contain a space!")
                app_name = None
                continue

        # Gets the app description
        if app_desc == None:
            app_desc = app.datareqs.get_desc()

        # Gets the port
        if port == None:
            port = app.datareqs.get_port()

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
        elif boundpath == "internal":
            boundpath = str(os.path.abspath(f"instances/{app_name}/content/"))

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

        # SSL is enabled by default for new apps. Its more secure, and is more true to the purpose of Pyhost this way
        # (Working immediately out-the-box)
        config_path = f"instances/{app_name}/config.json"
        # Sets the absolute path/boundpath in the json file
        config = web_config_dt
        jmod.setvalue(
            key="ssl_enabled",
            json_dir=config_path,
            value=True,
            dt=config
        )

        # Makes the appropriate directories
        os.makedirs(f"instances/{app_name}/", exist_ok=True)
        os.makedirs(f"instances/{app_name}/content/", exist_ok=True)
        # Copies all the content from the absolute path to the app's content folder using shutil
        if boundpath != f"instances/{app_name}/":
            shutil.copytree(boundpath, f"instances/{app_name}/content/", dirs_exist_ok=True)

        from .autostart import autostart
        # Sets the autostart and creates config.json if applicable
        if do_autostart:
            autostart.add(app_name)

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

        # Prints with green
        print("\033[92m" + f"Created app \"{app_name}\" successfully!" + "\033[0m")
        logging.info(f"Created app \"{app_name}\" successfully!")

    def create_wsgi(app_name:str=None, app_desc:str=None, port:int=None, boundpath:str=None, do_autostart:bool=True):
        '''
        the content file will always be named application.py and all the code in that file will be in a single function
        This function will create a WSGI app.
        '''
        
        if app_name == None or app_name == "":
            app_name = app.datareqs.get_name()
        if app_desc == None:
            app_desc = app.datareqs.get_desc()
        if port == None:
            port = app.datareqs.get_port()
        if boundpath == None:
            msg = (
                "\nThis directory will be copied to the app's content folder. You work on the project in this directory."
                "\nInternal binding will be: "+str(os.path.abspath(f"instances/{app_name}/application.py"))
                )
            while True:
                boundpath = app.datareqs.get_boundpath(
                    message=msg, inp_text="\nWhat is the full path to the app's python file? TEXT (Not optional) : "
                    )
                if boundpath == None:
                    print("Boundpath cannot be None!")
                    continue
                elif not boundpath.endswith(".py"):
                    print("The file must be a python file!")
                    continue
                break

        # Sets out the file structure
        os.makedirs(f"instances/{app_name}/", exist_ok=True)
        os.makedirs(f"instances/{app_name}/logs/", exist_ok=True)

        # Sets the config
        config_path = f"instances/{app_name}/config.json"
        app_config = wsgi_config_dt
        app_config["name"] = app_name
        app_config["description"] = app_desc
        app_config["port"] = port
        app_config["apptype"] = app.types.WSGI()
        app_config["boundpath"] = boundpath
        app_config["autostart"] = do_autostart
        with open(config_path, "w") as cf:
            json.dump(app_config, cf, indent=4)

        print(colours["green"]+ f"Created app \"{app_name}\" successfully!" + colours["white"])
        logging.info(f"Created app \"{app_name}\" successfully!")
        
        multiprocessing.Process(
            target=instance.start,
            name=f"{app_name}_wsgi",
            args=(app_name, True)
        )

    def delete(app_name:str=None, is_interface:bool=False, ask_confirmation:bool=True, del_backups:bool=None):
        if is_interface is True or app_name is None:
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

            # Asks if we should delete backups too
            if del_backups == None:
                while True:
                    try:
                        del_backups: str = input("Should the app's backups be deleted too? Y/N : ").lower()
                        if del_backups == "cancel":
                            print("Cancelled!")
                            return True
                        if "y" in del_backups:
                            del_backups = True
                        elif "n" in del_backups:
                            del_backups = False
                        else:
                            raise AssertionError("The autostart must be either 'Y' or 'N'!")
                        assert type(del_backups) is bool, "The autostart must be a boolean!"
                        break
                    except AssertionError as err:
                        print(str(err))
                        continue

        if ask_confirmation:
            try:
                inp = input(
                    f"\nAre you sure you want to delete \"{app_name}?\" Type the app's name to confirm.\nOtherwise, type cancel then press enter to cancel.\n---{colours['red']} {app_name}{colours['reset']}\n>>> {colours['red']}"
                )
                print(f"{colours['reset']}Confirmed!")
                if inp != app_name:
                    raise AssertionError("Cancelled!")
            except AssertionError as err:
                print(str(err))
                return
        
        # Deletes the app's folder
        shutil.rmtree(f"instances/{app_name}/")

        # Removes backups of the app if they exist
        # Gets the directory the backups are saved at
        if del_backups is True:
            backup_dir = jmod.getvalue(key="backup_dir", json_dir=setting_dir, dt=app_settings)
            if backup_dir == None: # None means nothing was set by the user as a preference
                backup_dir = instance.get_backup_dir(app_name)

            # Deletes the backups
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)

        # Prints in green
        print("\033[92m" + f"Deleted app \"{app_name}\" successfully!" + "\033[0m")
        logging.info(f"Deleted app \"{app_name}\" successfully!")

    def start_interface(app_name=None, is_interface=True):
        '''a def for the user to start an app from the command line easily via getting the app name from the user'''
        
        if is_interface is True and app_name is None:
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
        
        website = multiprocessing.Process(
            target=instance.start, args=(app_name, True),
            name=f"{app_name}_webserver"
            )
        website.start()
        pid = website.pid
        jmod.setvalue(
            key="pid",
            json_dir=f"instances/{app_name}/config.json",
            value=pid,
            dt=web_config_dt
        )

    def webserver(app_name=None, silent=True):
        '''
        If app_name is tuple/list, then it will use the first item as the config path and the second as the app name
        if app_name is str, it'll use the app_name as the app name and the config path will be instances/{app_name}/config.json

        silent = True will redirect stdout and stderr to /dev/null
        '''
        # Get the port from the config.json file
        config_path = os.path.abspath(f"instances/{app_name}/config.json")
        # Define the base directory for instances
        base_directory = os.path.abspath("instances/")

        # Construct the directory path for the specific app
        directory = os.path.join(base_directory, app_name)
        os.makedirs(directory, exist_ok=True)  # Create the directory if it doesn't exist
        
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
        notfoundpage_enabled = jmod.getvalue(
            key="404page_enabled",
            json_dir=config_path,
            default=False,
            dt=config_data
        )
        allow_dir_listing = jmod.getvalue(
            key="dir_listing",
            json_dir=config_path,
            default=False,
            dt=config_data
        )
        csp_directives = jmod.getvalue(
            key="csp_directives",
            json_dir=config_path,
            default=["Content-Security-Policy", "default-src 'self';","script-src 'self';",
                    "style-src 'self';","img-src 'self';","font-src 'self'"],
            dt=config_data
        )
        add_sec_heads = jmod.getvalue(
            key="do_securityheaders",
            json_dir=config_path,
            default=True,
            dt=config_data
        )
        serve_default = jmod.getvalue(
            key="serve_default",
            json_dir=config_path,
            default=True,
            dt=config_data
        )
        
        notfoundpage = jmod.getvalue(key="404page", json_dir=config_path, default="404.html", dt=config_data)

        # Define a custom request handler with logging
        class CustomHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                self.content_directory = config_data.get("contentloc")
                super().__init__(*args, directory=self.content_directory, **kwargs)

            if add_sec_heads:
                def add_security_headers(self):
                    # Add security headers based on user configuration
                    self.send_header("Content-Security-Policy", csp_directives)
                    self.send_header("Strict-Transport-Security", "max-age=31536000; includeSubDomains; preload")

            def do_GET(self):
                self.log_request_action()
                try:
                    warden = dict(jmod.getvalue(key="warden", json_dir=f"instances/{app_name}/config.json", dt=web_config_dt))
                    warden_enabled = warden.get("enabled", False)
                    wardened_dirs = warden.get("pages", None)
                except Exception as err:
                    logging.error(f"Failed to get warden settings for {app_name}: {err}")

                def ask_for_login():
                    # If PIN is not provided or incorrect, request PIN
                    with open("library/webpages/warden_login.html", "rb") as file:
                        content = file.read()
                        self.send_response(401)
                        self.send_header("Content-type", "text/html")
                        self.send_header("WWW-Authenticate", 'Bearer realm="pyhost", charset="UTF-8"')
                        self.end_headers()
                        self.wfile.write(content)

                if warden_enabled:
                    set_pin = warden.get("pin", None)
                    # If its -1, then it couldn't find the pin and the user needs to set it
                    pin_valid = self.path.find(f"/warden?pin={set_pin}") != -1
                    # Check if the requested path is wardened
                    logging.info(pin_valid)
                    if pin_valid is False:
                        for page_dir in wardened_dirs:
                            if page_dir == "*": # If its *, then all pages are wardened
                                # Ensures it is targetting a HTML file to prevent locking styling/js files
                                if self.path.endswith(".html") or self.path.endswith(".htm"):
                                    ask_for_login()
                                    return
                            if self.path == "/":
                                ask_for_login()
                                return
                            elif self.path == page_dir:
                                # If the requested path is wardened, serve the warden login page
                                ask_for_login()
                                return
                            else:
                                # Does not effect unwardened pages
                                if "/warden?pin=" in self.path:
                                    # return forbidden error
                                    self.send_error(403, "Warden Forbidden", "The requested path is forbidden.")
                                    return
                    else:
                        if self.path == f"/warden?pin={set_pin}": # This would mean its Root, set it to "/"
                            self.path = "/"
                        else:
                            self.path.replace(f"/warden?pin={set_pin}", "")
                            # Removes the pin from the path and continue on with the normal get request

                # Handle directory listing.
                # Handles it by making sure the request leads to a file and not a directory
                if not allow_dir_listing:
                    if self.path.endswith("/"):
                        # If the path is a directory and not the root, return a 403
                        if self.path != "/":
                            self.send_error(403, "Directory listing is disabled", "The requested path is a directory and directory listing is disabled. This has been banned in the security configuration of this pyhost instance.")
                            return

                # Check if the requested path is the root directory
                if self.path == "/":
                    # Serve the default_index as the landing page
                    # Get the absolute path of the default index file
                    default_index_path = os.path.abspath(os.path.join(self.content_directory, default_index))
                    
                    # Check if the default index file exists
                    if os.path.exists(default_index_path):
                        # Open the default index file and read its content
                        with open(default_index_path, 'rb') as index_file:
                            content = index_file.read()
                            
                            # Send a HTTP 200 OK response
                            self.send_response(200)
                            
                            # Set the Content-Type header to text/html
                            self.send_header("Content-type", "text/html")
                            self.end_headers()
                            
                            # Write the content to the response body
                            self.wfile.write(content)
                    else:
                        # If the default index file doesn't exist, serve the default HTML
                        self.serve_default_html()
                else:
                    # If the requested path is not the root directory
                    # Get the absolute path of the requested file
                    requested_file_path = os.path.abspath(os.path.join(self.content_directory, self.path.strip('/')))
                    
                    # Check if the requested file exists
                    if os.path.exists(requested_file_path):
                        # If the requested file exists, call the parent class's do_GET method
                        super().do_GET()
                    elif notfoundpage_enabled:
                        # If the requested file doesn't exist and a custom 404 page is enabled
                        if send_404:
                            # Get the absolute path of the custom 404 page
                            notfoundpage_path = os.path.abspath(os.path.join(self.content_directory, notfoundpage))
                        else:
                            # If the custom 404 page is not enabled, serve the default HTML and return
                            self.serve_default_html()
                            return
                        
                        # Check if the custom 404 page exists
                        if os.path.exists(notfoundpage_path):
                            # Open the custom 404 page and read its content
                            with open(notfoundpage_path, 'rb') as notfoundpage_file:
                                content = notfoundpage_file.read()
                                self.send_response(404)
                                # Set the Content-Type header to text/html
                                self.send_header("Content-type", "text/html")
                                self.end_headers()
                                
                                # Write the content to the response body
                                self.wfile.write(content)
                        else:
                            # If the custom 404 page doesn't exist, serve the default HTML
                            self.serve_default_html()
                    else:
                        # If the requested file doesn't exist and a custom 404 page is not enabled, serve the default HTML
                        self.serve_default_html()

            if serve_default:
                def serve_default_html(self):
                    # Get the path to the default HTML file
                    default_html_path = os.path.abspath(f"{root_dir}/library/webpages/default.html")
                    with open(default_html_path, 'rb') as default_html_file:
                        content = default_html_file.read()
                        # Replace placeholders in the HTML with actual values
                        content = content.replace(b"{{app_name}}", bytes(app_name, "utf-8"))

                        censored_content_dir = str(self.content_directory)
                        if censored_content_dir.startswith("C:\\Users\\"):
                            # Finds the next \ after "C:\Users\", then replaces the username with asterisks
                            user_end_index = censored_content_dir.find("\\", len("C:\\Users\\"))
                            if user_end_index != -1:
                                censored_content_dir = "C:\\Users\\****" + censored_content_dir[user_end_index:]
                        content = content.replace(b"{{content_dir}}", bytes(censored_content_dir, "utf-8"))

                    # Send the HTML content as a response
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(content)

            def log_request_action(self):
                # Get client address and requested file
                client_address = self.client_address[0]
                requested_file = self.path
                current_date = datetime.date.today().strftime("%Y-%m-%d")
                log_file_path = f"{base_directory}/{app_name}/logs/{current_date}.log"

                # Open the log file and write the request information
                with open(log_file_path, "a") as log_file:
                    if requested_file == "/":
                        log_file.write(f"{datetime.datetime.now()} - {app_name} - IP {client_address} requested {requested_file} (the landing page)\n")
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
                if jmod.getvalue(key="ssl_enabled", json_dir=config_path, dt=web_config_dt) == True:
                    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                    cert_dir = f"instances/{app_name}/cert.pem"
                    private_dir = f"instances/{app_name}/private.key"

                from .filetransfer import generate_ssl
                generate_ssl(cert_dir, private_dir)
                
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
                    dt=web_config_dt
                )

                # Start the server and keep it running until interrupted
                logging.info(f"Server \"{app_name}\" is now running on port {port}")
                httpd.serve_forever()

        except OSError as e:
            logging.error(f"Server \"{app_name}\" failed to start: {e}\n\n"+str(e.with_traceback(e.__traceback__)))
            if not silent:
                print(f"Server \"{app_name}\" failed to start: {e}\nIs there already something running on port {port}?")
            log_message(f"Server \"{app_name}\" failed to start: {e}\nIs there already something running on port {port}?")

    def start(app_name, silent=True): # Silent = True problem resolved :D
        '''Always run using Multiprocessing.Process()'''
        app_type = jmod.getvalue(key="apptype", json_dir=f"instances/{app_name}/config.json", dt=web_config_dt)

        # Starts the appropriate app type
        if app_type == app.types.webpage():
            instance.webserver(app_name, silent)
        elif app_type == app.types.WSGI():
            port = jmod.getvalue(key="port", json_dir=f"instances/{app_name}/config.json", dt=wsgi_config_dt)

            def StartFlask(app_dir, app_name):
                '''
                Create a WSGI Server set primarily for Flask.
                '''
                app = __import__(app_dir, fromlist=['']).app
                os.environ["FLASK_ENV"] = "production"  # Set Flask environment to production
                os.environ["FLASK_APP"] = app_name  # Set the name of your Flask app
                waitress.serve(app, host='0.0.0.0', port=port)
            # TODO: Add a way to get the app directory from the user and ACTUALLY implement this stuff

    def restart(app_name=None, is_interface=True):
        if is_interface == True or app_name == None:
            print("\n")
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
        multiprocessing.Process(
            target=instance.start,
            args=(app_name, True),
        ).start()
        print(f"Server \"{app_name}\" has started.")
        print("\033[92m" + f"Restarted app \"{app_name}\" successfully!" + "\033[0m")

    def get_status(app_name=None, is_interface=True):
        if is_interface == True or app_name == None:
            print("\n")
            for app in os.listdir("instances/"):
                if jmod.getvalue(key="running", json_dir=f"instances/{app}/config.json") == True:
                    print(app)
                    # Prints description in gray then resets to white
                    print("\033[90m" + str(jmod.getvalue(key="description", json_dir=f"instances/{app}/config.json")).replace("<nl>","\n") + "\033[0m")

            while True:
                print("\nEnter app name to get status.")
                app_name = input(">>> ")
                if app_name not in os.listdir("instances/"):
                    print("That app doesn't exist!")
                    continue
                else:
                    break

        # Gets the status
        running = jmod.getvalue(key="running", json_dir=f"instances/{app_name}/config.json", dt=web_config_dt)
        if is_interface:
            if running == True:
                print(f"Server \"{app_name}\" is running.")
            else:
                print(f"Server \"{app_name}\" is not running.")

        port = jmod.getvalue(key="port", json_dir=f"instances/{app_name}/config.json", dt=web_config_dt)

        if is_interface:
            if port != None:
                print(f"Server \"{app_name}\" is running on port {port}.")
            else:
                print(f"Server \"{app_name}\" is not running on a port.")
        
        warden_enabled = jmod.getvalue(key="warden.enabled", json_dir=f"instances/{app_name}/config.json", dt=web_config_dt)

        if is_interface:
            if warden_enabled == True:
                print(f"Server \"{app_name}\" has warden enabled.")
            else:
                print(f"Server \"{app_name}\" has warden disabled.")

        autostart = jmod.getvalue(key="autostart", json_dir=f"instances/{app_name}/config.json", dt=web_config_dt)

        if is_interface:
            if autostart == True:
                print(f"Server \"{app_name}\" will autostart.")
            else:
                print(f"Server \"{app_name}\" will not autostart.")

        return {"running": running, "port": port, "warden": warden_enabled,  "autostart": autostart}

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

    def stop(app_name, is_interface=True):
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
                    dt=web_config_dt
                )

                if is_interface: print(f"Server \"{app_name}\" has been stopped.")
                logging.info(f"Server \"{app_name}\" has been stopped.")
        except FileNotFoundError as e:
            print(f"Server \"{app_name}\" is not an existant app!")
            logging.error(f"Server \"{app_name}\" is not an existant app!")
        except Exception as e:
            print(f"Failed to stop server \"{app_name}\": {e}")
            logging.error(f"Failed to stop server \"{app_name}\": {e}")

    def update(app_name=None, is_interface=False):

        if is_interface == True or app_name == None:
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

                        outdated = instance.is_outdated(app_name=app, boundpath_only=True)

                        description = "\033[90m" + str(jmod.getvalue(key="description", json_dir=f"instances/{app}/config.json")).replace("<nl>","\n") + "\033[0m"
                        if outdated == False:
                            print("\033[96m" + app + "\033[0m\n"+description) # prints cyan
                        elif outdated == True:
                            print("\033[91m" + app + "\033[0m\n"+description) # Prints red
                        elif outdated == "nobp": # no boundpath result, stops it from looking in an old backup folder.
                            pass # don't print it, so the user doesn't see it as an option to do so
                        else:
                            print(app+"\n"+description)

                    app_name = input("\nPlease enter the app name to update. Press enter to refresh.\n>>> ")
                    if app_name == "cancel":
                        print("Cancelled!")
                        return True
                    elif app_name in os.listdir("instances/"):
                        break
                except PermissionError as err:
                    print("We encountered a permissions error while trying to read if an app is outdated!")
                    logging.error(str(err))
                    logging.error(str(err.with_traceback(err.__traceback__)))
                    return False
        
        # Overwrites internal with external directory
        boundpath = jmod.getvalue(key="boundpath", json_dir=f"instances/{app_name}/config.json")
        content_dir = jmod.getvalue(key="contentloc", json_dir=f"instances/{app_name}/config.json")
        # Takes a snapshot of the current content directory to back it up
        if os.listdir(content_dir) != []:
            if jmod.getvalue(key="do_autobackup", json_dir=setting_dir, dt=app_settings) == True:
                instance.backup(app_name=app_name, is_interface=False)
                print("Phase 1 completed: Snapshot taken.")
            else:
                print("Phase 1 Skipped: Auto Snapshots are disabled.")
        else:
            print("Phase 1 Skipped: Content directory is empty.")
        # Removes all old files and directories
        for item in os.listdir(content_dir):
            item_path = os.path.join(content_dir, item)
            try:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            except PermissionError as err:
                print("Permission error: Unable to remove a file or directory.")
                logging.error(str(err))
            except Exception as err:
                print("An error occurred while removing a file or directory:")
                print(str(err))
                # Logs the error
                logging.error(str(err))
        else:
            print("Update phase 2 completed: File removal.")
        # Updates all files
        shutil.copytree(src=boundpath, dst=content_dir, dirs_exist_ok=True)
        print("Phase 3 completed: File duplication\n"+"\033[92m"+"Update completed."+"\033[0m")
        jmod.setvalue(
            key="last_updated",
            json_dir=f"instances/{app_name}/config.json",
            value=time.time(),
            dt=web_config_dt
        )

    def is_outdated(app_name: str, boundpath_only: bool = False):
        '''
        returns a bool on if an app is outdated.
        if boundpath is True, it will return "nobp" if the user has not set an external bound path.
        '''
        def calculate_file_hash(file_path):
            BLOCKSIZE = 65536
            hasher = hashlib.sha1()
            file_path = str(file_path)
            if os.path.isdir(file_path) or file_path.endswith('.log'):
                return None
            with open(file_path, 'rb') as file:
                buf = file.read(BLOCKSIZE)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = file.read(BLOCKSIZE)
            file_hash = hasher.hexdigest()
            return file_hash

        def get_file_hashes(directory):
            file_hashes = {}
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, directory)
                    file_hash = calculate_file_hash(file_path)
                    if file_hash is not None:
                        file_hashes[relative_path] = file_hash
            return file_hashes

        boundpath = jmod.getvalue(key="boundpath", json_dir=f"instances/{app_name}/config.json")
        app_dir = jmod.getvalue(key="contentloc", json_dir=f"instances/{app_name}/config.json")

        # app_dir and boundpath start in the content_dir, so move 1 directory up.
        app_dir = os.path.abspath(os.path.join(app_dir, ".."))  # .. is up one directory
        boundpath = os.path.abspath(os.path.join(boundpath, ".."))

        # Changes the boundpath for if the app's boundpath == content_dir
        if boundpath_only == False:
            if boundpath == app_dir:
                boundpath = instance.get_backup_dir(app_name)  # returns something like .../pyhoster/backups/<appname>/(versions list, formatted as "ver<ver number>")

                # Gets the latest version
                highest_ver = len(os.listdir(boundpath))
                boundpath = os.path.join(boundpath, f"ver{highest_ver}/")  # Sets the boundpath to the highest version
        else:
            return "nobp"

        # Get the file hashes for each file in the external (boundpath) directory
        ext_hashes = get_file_hashes(boundpath)

        # Get the file hashes for each file in the internal (content_dir) directory
        int_hashes = get_file_hashes(app_dir)

        # Check for outdated files
        outdated = ext_hashes != int_hashes

        return outdated

    def get_backup_dir(app_name):
        # Gets the directory to backup the app instance to
        backup_dir = jmod.getvalue(key="backups_path", json_dir=setting_dir, dt=app_settings)
        if backup_dir != None: os.path.join(backup_dir,app_name)
        if backup_dir == None: # None means nothing was set by the user as a preference
            linux = os.name != "nt" # If the OS is linux, it will be true
            if linux:
                backup_dir = f"/etc/pyhoster/backups/{app_name}/"
            else:
                # Gets the appdata directory for the user
                appdata = os.getenv("APPDATA")
                backup_dir = f"{appdata}/pyhoster/backups/{app_name}/"
        backup_dir = os.path.abspath(backup_dir)
        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir

    def rollback(app_name=None, is_interface=False, rollback_ver=None):
        orange = "\033[93m"
        cyan = "\033[96m"
        green = "\033[92m"
        white = "\033[0m"
        gray = "\033[90m"
        
        if is_interface == True or app_name == None:
            timenow = time.time()
            while True:
                try:
                    print("\nAll app names below. Descriptions are in "+gray+"gray"+white)
                    print("Apps which were recently updated (4h ago maximum) are highlighed "+orange+"orange!"+white)
                    print(f"If the app was not updated recently, it will be highlighted {green}green{white}.")
                    print(f"And if we can't tell how long ago it was, we'll use {cyan}cyan{white}.\n")
                    for app in os.listdir("instances/"):
                        last_updated = jmod.getvalue(key="last_updated", json_dir=f"instances/{app}/config.json")
                        app_desc = str(jmod.getvalue(key="description", json_dir=f"instances/{app}/config.json")).replace("<nl>","\n")
                        if last_updated == None:
                            print(cyan+app+white)
                            print(gray+app_desc+white) # Time is unknown, print with cyan

                        elif last_updated != None:
                            # If its been less than 4 hours, print with orange
                            if timenow - last_updated <= 14400:
                                print(orange+app+white)
                                print(gray+app_desc+white)
                            else: # its been more than 4 hours, print with white
                                print(app)
                                print(gray+app_desc+white)

                    app_name = input("What is the name of the app you wish to rollback? TEXT : ").lower()
                    if app_name == "cancel":
                        print("Cancelled!")
                        return True
                    assert app_name in os.listdir("instances/"), "The app must exist to be rolled back!"
                    break
                except AssertionError as err:
                    print(str(err))
                    continue

        backup_dir = instance.get_backup_dir(app_name)

        # Creates the backup directory if it doesn't exist
        os.makedirs(backup_dir, exist_ok=True)
        # Lists out all the versions and their last modified time
        
        instance.stop(app_name=app_name) # stops the app, as its about to be overwritten
        
        if is_interface == True or rollback_ver == None:
            print(
            "\nAll snapshots of the app can be seen below. If it was recently added, its "+orange+"orange"+white+", else its "+green+"green"+white+"."
            )
            for version in os.listdir(backup_dir):
                try:
                    last_modified = os.path.getmtime(os.path.join(backup_dir, version))
                    if timenow - last_modified <= 14400:
                        print(orange+version+white)
                    else:
                        print(green+version+white)
                except:
                    print(version+" | WARNING: POTENTIALLY UNSTABLE! (Last modified time could not be found.)")

            while True:
                try:
                    rollback_ver = input("What version do you wish to rollback to? TEXT : ")
                    if rollback_ver == "cancel":
                        print("Cancelled!")
                        return True
                    assert rollback_ver in os.listdir(backup_dir), "The version must exist to be rolled back to!"
                    break
                except AssertionError as err:
                    print(str(err))
                    continue
        
        # Validates rollback_ver as a version
        try:
            assert rollback_ver in os.listdir(backup_dir), "The version must exist to be rolled back to!"
        except AssertionError as err:
            print(str(err))
            return
        
        # Completely overwrites current app with backup
        shutil.rmtree(f"instances/{app_name}/")
        print("Phase 1 completed.")
        shutil.copytree(src=os.path.join(backup_dir, rollback_ver), dst=f"instances/{app_name}/", dirs_exist_ok=True)
        print("Phase 2 completed.")

        # Starts the app again
        multiprocessing.Process(
            target=instance.start,
            args=(app_name, True),
            name=f"{app_name}_webserver",
        ).start()

        print(green+"Rollback completed!"+white)

    def backup(app_name=None, is_interface=True, do_alert=False):
        if app_name == None or is_interface == True:
            while True:
                try:
                    print("\n")
                    for app in os.listdir("instances/"):
                        print(app)
                        print("\033[90m"+str(jmod.getvalue(key="description", json_dir=f"instances/{app}/config.json")).replace("<nl>","\n")+"\033[0m")
                    else:
                        print("\nType Cancel to cancel the backup.")

                    app_name = input("What is the name of the app you wish to backup? TEXT : ").lower()
                    if app_name == "cancel":
                        print("Cancelled!")
                        return True
                    
                    assert app_name in os.listdir("instances/"), "The app must exist!"
                    break # Breaks the loop if it passes the assertion tests
                except AssertionError as err:
                    print(str(err))
                    continue
                    
        # Gets the directory to backup the app instance to
        backup_dir = instance.get_backup_dir(app_name)

        # Creates the backup directory if it doesn't exist
        os.makedirs(backup_dir, exist_ok=True)

        # Gets the version of the snapshot by listing the directory
        version = "ver"+str(len(os.listdir(backup_dir)) + 1)
        backup_dir = os.path.join(backup_dir, version) # Adds the version to the backup directory

        # Gets the directory of the app
        app_dir = os.path.abspath(f"instances/{app_name}/")
        try:
            # copies the app directory to the backup directory
            shutil.copytree(src=app_dir, dst=backup_dir, dirs_exist_ok=True)

            if do_alert == True or is_interface == True: 
                print(f"Snapshot of \"{app_name}\" completed! (Version {version})")
        except Exception as err:
            print(f"Failed to create snapshot of \"{app_name}\": {err}")

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
            try:
                with open (self.config_dir, "r") as config_file:
                    self.config_data = json.load(config_file)
            except FileNotFoundError:
                print("That app doesn't exist!")
                return

            # Stops the server if its not already stopped
            print("Stopping selected server for stability purposes.")
            instance.stop(self.app_name)

            self.take_command()

        def take_command(self):
            '''The def that handles input from the user on how to edit the app.'''
            while True:
                try:
                    print("What would you like to edit about the app?")
                    print("1. Name")
                    print("2. Port")
                    print("3. Description")
                    print("4. Boundpath")
                    print("5. Autostart")
                    print("6. Index Page")
                    print("7. 404 Page Settings")
                    print("8. Serve Default Page")
                    print("9. Security configuration")
                    print("10. Cancel\n")
                    option = input(">>> ").lower()
                    if option.isnumeric() == True:
                        # Handles for when the user uses a number to convert from number to text
                        choice_dict = {
                            1: "name",
                            2: "port",
                            3: "description",
                            4: "boundpath",
                            5: "autostart",
                            6: "index",
                            7: "404",
                            8: "doServeDefault",
                            9: "security",
                            10: "cancel",
                        }
                        option = choice_dict[int(option)]
                    
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
                    elif "404" in option:
                        self.page404_interface()
                        continue
                    elif "default" in option:
                        self.serve_default()
                        continue
                    elif "security" in option:
                        self.security_edit()
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
            print("Stopping edit...")
            startup = input("Would you like to start the app up? Y/N : ").lower()
            if "y" in startup:
                print(f"\"{self.app_name}\" started! (http://localhost:{jmod.getvalue('port', self.config_dir, default='FETCH_ERROR', dt=web_config_dt)})\nEdit completed and saved")
                multiprocessing.Process(
                    target=instance.start,
                    args=(self.app_name, True,),
                    name=f"{self.app_name}_webserver"
                ).start()
            elif "n" in startup:
                print("Edit completed and saved")
            else:
                print("Invalid answer.")

        def name(self, new_name=None):
            '''edits an apps name'''

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
                    dt=web_config_dt
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
                dt=web_config_dt
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
                dt=web_config_dt
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
                dt=web_config_dt
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
                dt=web_config_dt
            )
            print("Changed index file successfully!")

        def page404_interface(self):
            while True:
                try:
                    print("\nWhat would you like to edit about the 404 page? (Use numbers or text)")
                    print("1. Enabled (True/False)")
                    print("2. Filename (file_name.html)")
                    print("3. Cancel\n")
                    option = input(">>> ").lower()
                    # Seperates choices from args
                    try:
                        option, arg = option.split(" ", 1)
                        if arg != None or "":
                            has_arg = True
                    except:
                        has_arg = False
                        arg = None

                    if option.isnumeric() == True:
                        # Handles for when the user uses a number to convert from number to text
                        choice_dict = {
                            1: "enabled",
                            2: "filename",
                            3: "cancel",
                        }
                        option = choice_dict[int(option)]
                    
                    for word in option.split(" "):
                        if word in ["cancel", "stop", "exit", "quit"]:
                            print("Ending 404 edit...")
                            return True

                    # Handles the options for when the user does not use a number
                    if option == "enabled":
                        if has_arg:
                            self.page404_enabled(arg)
                        else:
                            self.page404_enabled(None)
                        continue
                    elif option == "filename":
                        if has_arg:
                            self.page404(arg)
                        else:
                            self.page404(None)
                        continue
                    else:
                        raise KeyError

                except AssertionError as err:
                    print(str(err))
                    continue
                except KeyError:
                    print("Invalid option!")
                    continue

        def page404_enabled(self, enabled=None):
            if enabled == "y":
                enabled = True
            elif enabled == "n":
                enabled = False

            if enabled == None:
                print("Set if the '404' page is enabled.\n")
                print('What is the 404 page? The 404 page is what shows up if the directory is not empty\nbut the requested file is not found.\n')
                print("This page is per-app, and disabled by default.\n")
                print("Do you want to enable the 404 page? Y/N : ")
                enabled = input('>>> ').lower()
                if enabled == "cancel":
                    print("Cancelled!")
                    return True
                if "y" in enabled:
                    enabled = True
                elif "n" in enabled:
                    enabled = False

            assert type(enabled) == bool
            jmod.setvalue(
                key="404page_enabled",
                json_dir=self.config_dir,
                value=enabled,
                dt=web_config_dt
            )
            print(f"404 page {'enabled' if enabled == True else 'disabled'} successfully! ")

        def page404(self, filename=None):
            if filename is None:
                while True:
                    try:
                        filename = input("What is the name of the 404 file? (Include file extension) : ")
                        assert filename != "", "The filename cannot be blank!"
                        assert "." in filename, "The filename must include a file extension!"
                        break
                    except AssertionError as err:
                        print(str(err))

            jmod.setvalue(
                key="404page",
                json_dir=self.config_dir,
                value=filename,
                dt=web_config_dt
            )
            print("Changed 404 file successfully!")

        def serve_default(self, do_serve=None):
            if do_serve == None:
                print("Set if the default page is served.")
                print('What is the default page? The default page is what shows up if the directory is empty.\n')
                print("This page is per-app, and enabled by default.")
                print("Do you want the default page? Y/N : ")
                while True: # Loop for retries.
                    do_serve = input('>>> ').lower()
                    if do_serve == "cancel":
                        print("Cancelled!")
                        return True
                    if "y" in do_serve:
                        do_serve = True
                        break
                    elif "n" in do_serve:
                        do_serve = False
                        break
                    else: # Retry logic
                        print("Invalid answer!")
                        continue

            assert type(do_serve) == bool
            jmod.setvalue(
                key="serve_default",
                json_dir=self.config_dir,
                value=do_serve,
                dt=web_config_dt
            )
            print(f"{colours['green']}Default page {'enabled' if do_serve == True else 'disabled'} successfully!{colours['reset']}")

        def security_edit(self):

            print("Welcome to security configuration. This menu is for advanced users only.")
            print("<!> Pyhost and its developers are not responsible for bad configurations or mis-management <!>\n")

            # Gets the current security settings then prints them out accordingly
            
            dir_listing = jmod.getvalue(key="dir_listing", json_dir=self.config_dir, dt=web_config_dt) # AKA autoindex I think
            securityheaders = jmod.getvalue(key="do_securityheaders", json_dir=self.config_dir, dt=web_config_dt)
            csp_directives = jmod.getvalue(key="csp_directives", json_dir=self.config_dir, dt=web_config_dt)
            
            print("Current settings:")
            # Dir listing
            if dir_listing == False:
                print(f"{colours['green']}1. Directory listing is disabled.")
            else:
                print(f"{colours['red']}1. Directory listing is enabled.")

            # Security headers
            if securityheaders == True:
                print(f"{colours['green']}2. Security headers are enabled.")
            else:
                print(f"{colours['red']}2. Security headers are disabled.")
            
            # CSP directives
            if csp_directives != None:
                if len(csp_directives) != 0:
                    print(f"{colours['green']}3. CSP directives are set.{colours['reset']}")
                else:
                    csp_directives = False
            else:
                csp_directives = False
            
            if not csp_directives: # Always reset colour at last print
                print(f"{colours['red']}3. CSP directives are not set.{colours['reset']}")

            choices_dict = {
                "1": "dir_listing",
                "2": "securityheaders",
                "3": "csp_directives",
            }
            while True:
                try:
                    print("\nWhat would you like to edit about the security configuration? (Use numbers or text)")
                    print("1. Directory listing")
                    print("2. Security headers")
                    print("3. CSP directives")
                    print("4. Cancel\n")
                    option = input(">>> ").lower()
                    # Seperates choices from args
                    try:
                        option, arg = option.split(" ", 1)
                        if arg != None or "":
                            has_arg = True
                    except:
                        has_arg = False
                        arg = None

                    if option.isnumeric() == True:
                        # Handles for when the user uses a number to convert from number to text
                        option = choices_dict[option]
                    
                    for word in option.split(" "):
                        if word in ["cancel", "stop", "exit", "quit"]:
                            print("Ending security edit...")
                            return True


                    options = self.security_options(
                        config_dir=self.config_dir,
                        app_name=self.app_name,
                    )
                    # Handles the options for when the user does not use a number
                    if option == "dir_listing":
                        if has_arg:
                            options.dir_listing(arg)
                        else:
                            options.dir_listing(None)
                        continue
                    elif option == "securityheaders":
                        if has_arg:
                            options.securityheaders(arg)
                        else:
                            options.securityheaders(None)
                        continue
                    elif option == "csp_directives":
                        if has_arg:
                            options.csp_directives(arg)
                        else:
                            options.csp_directives(None)
                        continue
                    else:
                        raise KeyError("Invalid option!")

                except AssertionError as err:
                    print(str(err))
                    continue
                except KeyError:
                    print("Invalid option!")
                    continue

        class security_options():
            def __init__(self, app_name, config_dir=None) -> None:
                self.app_name = app_name

                if config_dir == None:
                    self.config_dir = os.path.abspath(f"instances/{app_name}/config.json")
                else:
                    self.config_dir = config_dir

            def dir_listing(self, enabled=None):
                if enabled == None:
                    print("Set if the directory listing is enabled.")
                    print('What is the directory listing? The directory listing is what shows up if the directory is empty.\n')
                    print("This page is per-app, and enabled by default.")
                    print("Do you want the directory listing? Y/N : ")
                    while True: # Loop for retries.
                        enabled = input('>>> ').lower()
                        if enabled == "cancel":
                            print("Cancelled!")
                            return True
                        if "y" in enabled:
                            enabled = True
                            break
                        elif "n" in enabled:
                            enabled = False
                            break
                        else: # Retry logic
                            print("Invalid answer!")
                            continue

                assert type(enabled) == bool
                jmod.setvalue(
                    key="dir_listing",
                    json_dir=self.config_dir,
                    value=enabled,
                    dt=web_config_dt
                )

                print(f"{colours['green']}Directory listing {'enabled' if enabled == True else 'disabled'} successfully!{colours['reset']}")

            def securityheaders(self, enabled=None):
                if enabled == None:
                    print("Set if the security headers are enabled.")
                    print('What are the security headers? The security headers are what show up in the response headers.\n')
                    print("This page is per-app, and disabled by default.")
                    print("Do you want the security headers? Y/N : ")
                    while True: # Loop for retries.
                        enabled = input('>>> ').lower()
                        if enabled == "cancel":
                            print("Cancelled!")
                            return True
                        if "y" in enabled:
                            enabled = True
                            break
                        elif "n" in enabled:
                            enabled = False
                            break
                        else: # Retry logic
                            print("Invalid answer!")
                            continue

                assert type(enabled) == bool
                jmod.setvalue(
                    key="do_securityheaders",
                    json_dir=self.config_dir,
                    value=enabled,
                    dt=web_config_dt
                )

                print(f"{colours['green']}Security headers {'enabled' if enabled == True else 'disabled'} successfully!{colours['reset']}")

            def csp_directives(self, directives=None):
                '''
                Prints out (from the list in the json file) all the csp directives.
                If the user provides an argument, it will add it to the list. Also lets the user remove directives.
                Asks is the user wants to remove or add a directive before doing so
                '''
                if directives is None:
                    directives = []

                csp_directives_list = jmod.getvalue(
                    key="csp_directives",
                    json_dir=self.config_dir,
                    dt=web_config_dt,
                    default=["Content-Security-Policy", "default-src 'self';","script-src 'self';",
                             "style-src 'self';","img-src 'self';","font-src 'self'"]
                    )

                no_csp = False
                if csp_directives_list == None or csp_directives_list == []:
                    print("\nNo CSP directives are set. Lets add some")
                    csp_directives_list = []
                    no_csp = True
                else:
                    csp_directives_list = list(csp_directives_list)

                if directives and no_csp is False:
                    csp_directives_list.extend(directives)

                    print("Current CSP directives:")
                    for directive in csp_directives_list:
                        print(directive)

                while True:
                    if not no_csp:
                        user_input = input("Do you want to add or remove a directive? (add/remove/quit): ").lower()
                    else:
                        user_input = "add" # Forces add if no csp directives are set
                    
                    print("\nType Cancel to cancel, type Done to finish editing.\n")
                    if user_input == "add":
                        new_directive = input("Enter the directive you want to add: ")
                        csp_directives_list.append(new_directive)
                        print(f"{colours['green']}CSP directive added.{colours['reset']}")
                    
                    elif user_input == "remove":
                        for i, directive in enumerate(csp_directives_list):
                            print(f"{i + 1}. {directive}")
                        remove_directive = input("Enter the directive you want to remove: ")
                        if remove_directive in csp_directives_list:
                            csp_directives_list.remove(remove_directive)
                            print(f"{colours['green']}CSP directive removed.{colours['reset']}")
                        else:
                            print("Directive not found.")
                    
                    elif user_input == "cancel":
                        print("Cancelled!")
                        return True
                    
                    else:
                        print("Invalid input. Please enter 'add', 'remove', or 'quit'.")
                        continue

                jmod.setvalue(
                    key="csp_directives",
                    json_dir=self.config_dir,
                    value=csp_directives_list,
                    dt=web_config_dt
                )

                return csp_directives_list