import os, json, logging, sys, datetime, socketserver, http.server
import webbrowser
from ..jmod import jmod
from ..data_tables import app_settings, web_config_dt
root_dir = os.getcwd()
setting_dir = "settings.json"
import multiprocessing

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

class webcontroller:
    def run(silent_gui=True):
        if silent_gui == -1:
            silent_gui = jmod.getvalue(
                key="webgui.silent",
                json_dir=setting_dir,
                default=True,
                dt=app_settings
            )

        webgui_thread = multiprocessing.Process(
            target=webcontroller.startgui, args=(silent_gui,)
        )
        webgui_thread.start()
        port = jmod.getvalue(key="webgui.port", json_dir=setting_dir, default=4040, dt=app_settings)
        print(f"<--WebGUI is now running on \"http://localhost:{port}\"-->")
        jmod.setvalue(
            key="webgui.pid",
            json_dir="settings.json",
            value=webgui_thread.pid,
            dt=app_settings
        )

    def startgui(silent=True):
        '''
        If app_name is tuple/list, then it will use the first item as the config path and the second as the app name
        if app_name is str, it'll use the app_name as the app name and the config path will be instances/{app_name}/config.json

        silent = True will redirect stdout and stderr to /dev/null
        '''
        # Get the port from the config.json file
        config_path = os.path.abspath(f"library/WebGUI/config.json")
        if not os.path.exists(config_path):
            with open(config_path, 'w') as config_file:
                web_config_dt["port"] = 4040
                web_config_dt["name"] = "WebGUI"
                web_config_dt["description"] = "The WebGUI is a web interface for PyHost. It allows you to manage your apps and settings from a web browser."
                web_config_dt["contentloc"] = "library/WebGUI/content/"
                json.dump(web_config_dt, config_file, indent=4, separators=(',', ': '))

        with open(config_path, 'r') as config_file:
            config_data: dict = json.load(config_file)
        port = config_data.get("port", 4040)

        if port is None:
            print(f"Port is not defined in config.json for WebGUI!")
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
        notfoundpage = jmod.getvalue(
            key="404page",
            json_dir=config_path,
            default="404.html",
            dt=config_data
            )

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
                    warden = dict(jmod.getvalue(key="warden", json_dir=config_path, dt=web_config_dt))
                    warden_enabled = warden.get("enabled", False)
                    wardened_dirs = warden.get("pages", None)
                except Exception as err:
                    logging.error(f"Failed to get warden settings for WebGUI: {err}")

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
                        content = content.replace(b"{{app_name}}", bytes("PyHost WebGUI", "utf-8"))

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
                log_file_path = f"logs/WebGUI/{current_date}.log"
                os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

                # Open the log file and write the request information
                with open(log_file_path, "a") as log_file:
                    if requested_file == "/":
                        log_file.write(f"{datetime.datetime.now()} - WebGUI - IP {client_address} requested {requested_file} (the landing page)\n")
                    else:
                        log_file.write(f"{datetime.datetime.now()} - WebGUI - IP {client_address} requested file {requested_file}\n")

        # Define a custom log message function
        def log_message(message):
            current_date = datetime.date.today().strftime("%Y-%m-%d")
            log_file_path = os.path.abspath(f"logs/WebGUI/{current_date}.log")

            os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
            with open(log_file_path, "a") as log_file:
                log_file.write(f"{datetime.datetime.now()} - WebGUI - {message}\n")

        # Redirect stdout and stderr to /dev/null if silent is True
        if silent:
            sys.stdout = open(os.devnull, "w")
            sys.stderr = open(os.devnull, "w")

        try:
            # Create a socket server with the custom handler
            with socketserver.TCPServer(("", port), CustomHandler) as httpd:
                # Print a message to indicate the server has started unless silent is True
                if not silent:
                    print(f"WebGUI is running on port {port}. Check the logs for actions.\n"
                        f"You can visit it on http://localhost:{port}")

                log_message(f"WebGUI is running.")
                # Get the PID of the current thread (web server)

                # Sets server to running in JSON file and save the PID
                jmod.setvalue(
                    key="running",
                    json_dir=config_path,
                    value=True,
                    dt=web_config_dt
                )

                # Start the server and keep it running until interrupted
                logging.info(f"WebGUI is now running on port {port}")
                httpd.serve_forever()

        except OSError as e:
            logging.error(f"WebGUI failed to start: {e}\n\n"+str(e.with_traceback(e.__traceback__)))
            if not silent:
                print(f"WebGUI failed to start: {e}\nIs there already something running on port {port}?")
            log_message(f"WebGUI failed to start: {e}\nIs there already something running on port {port}?")
    
    def stopgui():
        # Get the PID of the WebGUI
        webgui_pid = jmod.getvalue(
            key="webgui.pid",
            json_dir=setting_dir,
            default=-1,
            dt=app_settings
        )

        # If the WebGUI is not running, return False
        if webgui_pid == -1:
            return False

        # Kill the WebGUI process
        try:
            os.kill(webgui_pid, 2)
        except:
            try:
                os.kill(webgui_pid, 9)
            except:
                return False
        logging.info(f"WebGUI has been stopped.")
        return True
    
    def is_running():
        # Get the running status of the WebGUI
        return jmod.getvalue(
            key="webgui.pid",
            json_dir=setting_dir,
            default=False,
            dt=web_config_dt
        ) != None
    
    def status(interface:bool):
        # Get the running status of the WebGUI
        running = webcontroller.is_running()
        if not interface:
            if running is False:
                print("The WebGUI is not running.")
                return
            else:
                print("The WebGUI is running.")

        port = jmod.getvalue(
            key="port",
            json_dir=setting_dir,
            default=4040,
            dt=web_config_dt
        )
        if interface: print(f"The WebGUI Is bound to Port {port}")
        return {"running": running, "port": port}
    
    def enter():
        # Get the port of the WebGUI
        port = jmod.getvalue(
            key="webgui.port",
            json_dir=setting_dir,
            default=4040,
            dt=web_config_dt
        )
        hostname = jmod.getvalue(
            key="webgui.hostname",
            json_dir=setting_dir,
            default="localhost",
            dt=web_config_dt
        )
        running = webcontroller.is_running()

        while True: # Retry logic
            try:
                print("\n<--Pyhost WebGUI Interface. Type EXIT to exit. -->")
                print(f"WebGUI is running at http://{hostname}:{port}" if running else f"WebGUI is not running but set for port {port}.")
                print("Enter 'help' to see a list of commands.")
                cmd = input(f"{colours['red' if not running else 'green']}webgui{colours['reset']}> ").lower()
                if cmd == "exit":
                    break
                elif cmd == "help":
                    webcontroller.help_msg()
            except AssertionError as err:
                print(str(err))
            
        return True

    def help_msg():
        print("<!----WebGUI Help---->")
        print("help - Shows this message")
        print("exit - Exits the WebGUI Command Line Interface")
        print("start - Starts the WebGUI")
        input("Press enter to continue or enter any text...")


    def open_gui():
        # Get the port of the WebGUI
        port = jmod.getvalue(
            key="webgui.port",
            json_dir=setting_dir,
            default=4040,
            dt=web_config_dt
        )
        # Assume LocalHost as this function can't open a remote GUI on a different machine.
        webbrowser.open(f"http://localhost:{port}", 2)