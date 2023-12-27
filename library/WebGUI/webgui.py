import os, json, sys, datetime, socketserver, http.server
import webbrowser
import ssl
import time
try:
    from ..jmod import jmod
    from ..data_tables import app_settings, web_config_dt
except ImportError as err:
    print("Hello! To run Pyhost, you must run the file pyhost.py located in this projects root directory, not this file.\nThank you!")
    from pylog import pylog
    pylog().error(f"Import error in {__name__}", err)
root_dir = os.getcwd()
setting_dir = "settings.json"
import multiprocessing

from ..pylog import pylog
pylogger = pylog()

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
    def run(silent_gui=True, show_interface=True):
        '''
        Starts the WebGUI on a thread. This is the proper way to start the WebGUI.
        
        silent_gui = True will redirect stdout and stderr to /dev/null
        show_interface = True will print the "WebGUI is now running on port {port}" message

        if silent_gui is -1, it will use the value from settings.json

        Returns -1 if the WebGUI is already running
        '''
        if webcontroller.is_running():
            if show_interface:
                print("The WebGUI is already running.")
            return -1
        
        # Checks if the API is running
        if not jmod.getvalue(key="api.running", json_dir=setting_dir, default=False, dt=app_settings):
            print(f"{colours['red']}The API is not running. Without the API, the website can't interact with PyHost. Please start it.{colours['white']}")
            print(f"{colours['green']}Instructions:")
            print(f"{colours['green']}1. Go to the main menu (by typing exit)")
            print(f"{colours['green']}2. enter command \"API\"")
            print(f"{colours['green']}3. enter command \"start\"")
            print(f"{colours['green']}If you want it to start on autoboot, enter command \"autoboot\" then select Y{colours['white']}")
            pylogger.warning("The API is not running. Please start the API before starting the WebGUI.")
            input("Press enter to continue...")

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
        time.sleep(0.25) # Wait for the server to start
        port = jmod.getvalue(key="webgui.port", json_dir=setting_dir, default=4040, dt=app_settings)
        hostname = jmod.getvalue(key="hostname", json_dir=setting_dir, default="localhost", dt=app_settings)
        if hostname == -1:
            hostname = "localhost"
        print(f"<--WebGUI is now running on \"https://{hostname}:{port}\"-->")
        jmod.setvalue(
            key="webgui.pid",
            json_dir="settings.json",
            value=webgui_thread.pid,
            dt=app_settings
        )

    def startgui(silent=True):
        '''
        Runs the webserver.
        If app_name is tuple/list, then it will use the first item as the config path and the second as the app name
        if app_name is str, it'll use the app_name as the app name and the config path will be instances/{app_name}/config.json

        silent = True will redirect stdout and stderr to /dev/null
        '''
        debug = False
        webgui_logger = pylog(
            logform='WEBGUI | %loglevel% - %time% - %file% | '
        )

        # Get the port from the config.json file
        config_path = os.path.abspath(f"library/WebGUI/config.json")
        if not os.path.exists(config_path):
            with open(config_path, 'w') as config_file:
                web_config_dt["port"] = 4040
                web_config_dt["name"] = "WebGUI"
                web_config_dt["description"] = "The WebGUI is a web interface for PyHost. It allows you to manage your apps and settings from a web browser."
                web_config_dt["contentloc"] = "library/WebGUI/content/"
                json.dump(web_config_dt, config_file, indent=4, separators=(',', ': '))

        port = jmod.getvalue(key="webgui.port", json_dir=setting_dir, default=4040, dt=app_settings)
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
            dt=app_settings
        )
        notfoundpage_enabled = jmod.getvalue(
            key="404page_enabled",
            json_dir=config_path,
            default=False,
            dt=app_settings
        )
        allow_dir_listing = jmod.getvalue(
            key="dir_listing",
            json_dir=config_path,
            default=False,
            dt=app_settings
        )
        csp_directives = jmod.getvalue(
            key="csp_directives",
            json_dir=config_path,
            default=["Content-Security-Policy", "default-src 'self';","script-src 'self';",
                    "style-src 'self';","img-src 'self';","font-src 'self'"],
            dt=app_settings
        )
        add_sec_heads = jmod.getvalue(
            key="do_securityheaders",
            json_dir=config_path,
            default=True,
            dt=app_settings
        )
        serve_default = jmod.getvalue(
            key="serve_default",
            json_dir=config_path,
            default=True,
            dt=app_settings
        )  
        notfoundpage = jmod.getvalue(
            key="404page",
            json_dir=config_path,
            default="404.html",
            dt=app_settings
            )

        # Define a custom request handler with logging
        class CustomHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                self.content_directory = "library/WebGUI/content/"
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
                    pylogger.error(f"Failed to get warden settings for WebGUI: {err}", err)

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
                        return True
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
                # Open the log file and write the request information
                if requested_file == "/":
                    webgui_logger.info(f"{datetime.datetime.now()} - WebGUI - IP {client_address} requested {requested_file} (the landing page)\n")
                else:
                    webgui_logger.info(f"{datetime.datetime.now()} - WebGUI - IP {client_address} requested file {requested_file}\n")

        # Redirect stdout and stderr to /dev/null if silent is True
        if not debug:
            sys.stdout = open(os.devnull, "w")
            sys.stderr = open(os.devnull, "w")

        try:
            # Create a socket server with the custom handler
            with socketserver.TCPServer(("", port), CustomHandler) as httpd:

                # Sets server to running in JSON file
                jmod.setvalue(
                    key="running",
                    json_dir=config_path,
                    value=True,
                    dt=web_config_dt
                )

                if jmod.getvalue(config_path, "ssl_enabled", True, app_settings):
                    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                    cert_dir = "library/WebGUI/cert.pem"
                    private_dir = "library/WebGUI/private.key"

                    from ..filetransfer import generate_ssl
                    generate_ssl(cert_dir, private_dir)

                    context.load_cert_chain(cert_dir, private_dir)
                    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
                    webgui_logger.info(f"WebGUI is running with SSL.")
                else:
                    webgui_logger.info(f"WebGUI is running without SSL.")

                # Start the server and keep it running until interrupted
                webgui_logger.info(f"WebGUI is now running on port {port}")
                httpd.serve_forever()
                # Once it reaches here, it stops.
                webgui_logger.info("WebGUI has been stopped.")
                return True
        except OSError as err:
            webgui_logger.error(f"WebGUI failed to start!", err)
            if not silent:
                print(f"WebGUI failed to start: {err}\nIs there already something running on port {port}?")
        except KeyboardInterrupt:
            webgui_logger.info("WebGUI has been stopped.")
            return True

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
        pylogger.info(f"WebGUI has been stopped.")

        jmod.setvalue(
            key="webgui.pid",
            json_dir=setting_dir,
            value=None,
            dt=web_config_dt
        )

        print("<--WebGUI has been stopped-->")
        time.sleep(0.5)
        return True
    
    def is_running():
        # Get the running status of the WebGUI
        pid = jmod.getvalue(
            key="webgui.pid",
            json_dir=setting_dir,
            default=None,
            dt=web_config_dt
        )
        if pid is None:
            return False
        else:
            return True
    
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
            key="webgui.port",
            json_dir=setting_dir,
            default=4040,
            dt=web_config_dt
        )
        if interface: print(f"The WebGUI Is bound to Port {port}")
        return {"running": running, "port": port}
    
    def enter():
        while True: # Retry logic
            # Get the port of the WebGUI
            port = jmod.getvalue(
                key="webgui.port",
                json_dir=setting_dir,
                default=4040,
                dt=web_config_dt
            )
            hostname = jmod.getvalue(
                key="hostname",
                json_dir=setting_dir,
                default="localhost",
                dt=web_config_dt
            )
            running = webcontroller.is_running()
            do_ssl = "s" if jmod.getvalue(
                key="ssl_enabled",
                json_dir="library/WebGUI/config.json",
                default=True,
                dt=web_config_dt
            ) else ""

            try:
                print("\n<--Pyhost WebGUI Interface. Type EXIT to exit. -->")
                print(f"WebGUI is running at http{do_ssl}://{hostname}:{port}" if running else f"WebGUI is not running but set for port {port}.")
                print("Enter 'help' to see a list of commands.")
                cmd = input(f"{colours['red' if not running else 'green']}webgui{colours['reset']}> ").lower()
                if cmd == "exit":
                    break
                elif cmd == "help":
                    webcontroller.help_msg()
                elif cmd == "start":
                    webcontroller.run()
                elif cmd == "stop":
                    webcontroller.stopgui()
                elif cmd == "status":
                    webcontroller.status(interface=True)
                elif "port" in cmd: # uses "in" instead of == to allow for "set port", "setport", etc.
                    port = input("Enter the port to set the WebGUI to: ")
                    webcontroller.setport(port)
                elif cmd == "hostname":
                    webcontroller.sethostname()
                elif cmd == "open":
                    webcontroller.open_gui()
                elif cmd == "autoboot":
                    webcontroller.autoboot()
                elif cmd == "cls":
                    from ..application import application # Import here to prevent circular imports
                    application.clear_console()
                    del application
                else:
                    print("Unknown command")
            except AssertionError as err:
                print(str(err))
            
        return True

    def help_msg():
        print("<----WebGUI Help---->")
        print("help - Shows this message")
        print("exit - Exits the WebGUI Command Line Interface")
        print("start - Starts the WebGUI")
        print("stop - Stops the WebGUI")
        print("status - Shows the status of the WebGUI")
        print("port - Sets the port of the WebGUI")
        print("hostname - Sets the hostname of the WebGUI")
        print("open - Opens the WebGUI in your default browser")
        print("autoboot - Sets if the WebGUI to start on boot")
        print("cls - Clears the screen")
        print("<----End of Help---->")

        input("Press enter to continue or enter any text...")

    def autoboot(do_autoboot=None, interface=True):
        '''
        Sets the WebGUI to start on boot
        '''
        if interface or do_autoboot == None:
            while True:
                do_autoboot = input("Do you want the WebGUI to start on boot? (Y/N): ").lower()
                if do_autoboot == "y":
                    do_autoboot = True
                    break
                elif do_autoboot == "n":
                    do_autoboot = False
                    break
                else:
                    print("Invalid input")

        jmod.setvalue(
            key="webgui.autoboot",
            json_dir=setting_dir,
            value=do_autoboot,
            dt=web_config_dt
        )
        if interface: print(f"WebGUI autoboot has been set to {do_autoboot}")
        pylogger.info(f"WebGUI autoboot has been set to {do_autoboot}")
        return True

    def setport(port=None, interface=True):
        '''
        Sets the port of the WebGUI
        '''
        if port == None:
            from ..application import application # Import here to prevent circular imports
            port = application.datareqs.get_port()
            del application

        jmod.setvalue(
            key="webgui.port",
            json_dir=setting_dir,
            value=port,
            dt=web_config_dt
        )
    
        if interface: print(f"WebGUI port has been set to {port}")
        pylogger.info(f"WebGUI port has been set to {port}")
        return True
    
    def sethostname(hostname=None, interface=True):
        '''
        Sets the hostname of the WebGUI
        '''
        if hostname == None:
            from ..application import application
            hostname = application.datareqs.get_hostname()
            del application
        
        if isinstance(hostname, str):
            jmod.setvalue(
                key="hostname",
                json_dir=setting_dir,
                value=hostname,
                dt=web_config_dt
            )

            if interface: print(f"WebGUI hostname has been set to {hostname}")
            pylogger.info(f"WebGUI hostname has been set to {hostname}")
            return True
        else:
            if interface: print("Hostname must be a string!")
            pylogger.warning("User tried to set hostname, but Hostname must be a string! Entered value: "+str(hostname))
            return False

    def open_gui():
        '''
        Opens the WebGUI in the default browser
        '''
        print("Opening WebGUI in your default browser...")
        # Get the port of the WebGUI
        port = jmod.getvalue(
            key="webgui.port",
            json_dir=setting_dir,
            default=4040,
            dt=web_config_dt
        )
        # Assume LocalHost as this function can't open a remote GUI on a different machine.
        webbrowser.open(f"https://localhost:{port}/login.html", 2)

class webgui_files:
    def update_connection_details():
        '''
        Updates the connection details in the WebGUI's files by finding Where the IP:PORT is and updating it.
        This way, no need for placeholders or mid-transaction editing.

        Returns True if successful, False if not. 
        '''
        # Get the connection details from the settings.json file
        hostname = jmod.getvalue(
            key="hostname",
            json_dir=setting_dir,
            default="localhost",
            dt=web_config_dt
        )
        port = jmod.getvalue(
            key="api.port",
            json_dir=setting_dir,
            default=4000,
            dt=web_config_dt
        )
        # TODO: Add SSL support to the API
        protocal = "http" # This will be configurable to ssl later

        # Goes through every JS and HTML file in the content directory
        content_dir = "library/WebGUI/content/"
        for root, _, files in os.walk(content_dir):
            for file in files:
                # Finds where the IP:PORT is and replaces it with the new IP:PORT
                # IP and Port will normally be in the context of a fetch request to the API
                # Here, we do not assume that we will find the default "http://localhost:4000" as this function may have
                # Been ran in the past.
                if file.endswith(".js"):
                    # Open the file and read its content
                    with open(os.path.join(root, file), "r") as readfile:
                        content = readfile.read()
                    
                    filelines = content.splitlines()
                    # Finds the index of where the IP should begin
                    for line in filelines.copy():
                        jsfetch_index = line.find("fetch(")
                        if jsfetch_index != -1:
                            # We have found one instance of fetch, we will assume the IP and port are on the same line as this fetch
                            # Gets rid of content before fetch index
                            jsfetch_index = line.find("fetch(")+7 # Removes everything before the http://
                            endfetch_index = line.find(", {")-1 # Finds the end of the fetch request. This is what it normally looks like
                            # Extracts the IP and port from the range
                            ip_port = line[jsfetch_index:endfetch_index]
                            # Extract protocol
                            old_protocol = ip_port[:ip_port.find("://")]

                            # Remove the protocol part to get the rest of the URL
                            url_without_protocol = ip_port[len(old_protocol) + 3:]

                            # Extract hostname
                            old_hostname = url_without_protocol[:url_without_protocol.find(":")]

                            # Extract port
                            old_port_index = url_without_protocol.find(":") + 1
                            old_port_end_index = old_port_index
                            while old_port_end_index < len(url_without_protocol) and url_without_protocol[old_port_end_index].isdigit():
                                old_port_end_index += 1
                            old_port = url_without_protocol[old_port_index:old_port_end_index]

                            newUrl = f"{protocal}://{hostname}:{port}"
                            oldUrl = f"{old_protocol}://{old_hostname}:{old_port}"
                            break
                    
                    # Replaces all instances of the old IP:PORT with the new IP:PORT
                    content = content.replace(oldUrl, newUrl)
                    # Now we update the file
                    with open(os.path.join(root, file), "w") as writingtofile:
                        writingtofile.write(content)
