import http.server, socketserver, os, datetime, sys

def start_custom_web_server(port, directory, app_name, silent=True):
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

    # Change to the specified directory and serve from there
    os.chdir(directory)

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
            print(f"Server is running. Check the logs for actions.")

        # Start the server and keep it running until interrupted
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

start_custom_web_server(8080, "./beta/testweb", "mytestapp", silent=True)
# A Function I am developing to replace nginx. Not working on main app for now