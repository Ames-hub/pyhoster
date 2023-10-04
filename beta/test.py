import http.server
import socketserver
import os
import datetime
import sys
import threading

def start_custom_web_server(port, directory, app_name, silent=True):
    '''
    A Function which can initialize a already created webserver folder and serve the files.
    port: The port to serve the files on
    directory: The directory to serve the files from. (Auto normally, but can be overriden here.)
    app_name: The name of the app to be used in the logs
    '''
    os.chdir(directory)
    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            # Log the request action to a log file
            self.log_request_action()
            super().do_GET()

        def log_request_action(self):
            # Get the client's IP address
            client_address = self.client_address[0]
            requested_file = self.path
            current_date = datetime.date.today().strftime("%Y-%m-%d")
            log_file_path = f"logs/{current_date}.log"
            # Converts log_file_path to an absolute path
            log_file_path = os.path.abspath(log_file_path)

            with open(log_file_path, "a") as log_file:
                if requested_file == "/":
                    log_file.write(f"{datetime.datetime.now()} - {app_name} - IP {client_address} requested the landing page\n")
                else:
                    log_file.write(f"{datetime.datetime.now()} - {app_name} - IP {client_address} requested file {requested_file}\n")

    def log_message(message):
        current_date = datetime.date.today().strftime("%Y-%m-%d")
        with open(f"logs/{current_date}.log", "a") as log_file:
            log_file.write(f"{datetime.datetime.now()} - {app_name} - {message}\n")

    # Create the log directory if it doesn't exist
    log_directory = f"logs/"
    os.makedirs(log_directory, exist_ok=True)

    # Redirect stdout and stderr to /dev/null if silent is True
    if silent:
        sys.stdout = open(os.devnull, "w")
        sys.stderr = open(os.devnull, "w")

    # Create a socket server with the custom handler
    with socketserver.TCPServer(("", port), CustomHandler) as httpd:
        # Print a message to indicate the server has started unless silent is True
        if not silent:
            print(f"Server \"{app_name}\" is running. Check the logs for actions.\n"\
                  f"You can visit it on http://localhost:{port}")
            
        log_message(f"Server \"{app_name}\" is running.")

        # Start the server and keep it running until interrupted
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            if not silent: print(f"\nServer \"{app_name}\" stopped.")
            log_message(f"Server \"{app_name}\" stopped.")

# Use absolute paths for both directories
directory1 = os.path.abspath("./beta/testweb")
directory2 = os.path.abspath("./beta/testweb2")

# Run two instances of the web server concurrently
threading.Thread(
    target=start_custom_web_server,
    args=(8080, directory1, "mytestapp", False)).start()

threading.Thread(
    target=start_custom_web_server,
    args=(8081, directory2, "mytestapp2", False)).start()

# A Function I am developing to replace nginx. Not working on main app for now