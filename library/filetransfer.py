import os
import ssl
import logging
import multiprocessing
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import ThreadedFTPServer
from datetime import datetime, timedelta
from .jmod import jmod
from .data_tables import app_settings, new_user

colours = {
    "reset": "\u001b[0m",
    "black": "\u001b[30m",
    "red": "\u001b[31m",
    "green": "\u001b[32m",
    "yellow": "\u001b[33m",
    "blue": "\u001b[34m",
    "magenta": "\u001b[35m",
    "cyan": "\u001b[36m",
    "white": "\u001b[37m",
    "gray": "\u001b[90m",
}

class ftp:
    def start(certfile=None, prvkeyfile=None, server_port=None, use_ssl=True, bypass_enabled=False):
        # Create a logger
        ftp_logger = logging.getLogger('ftp')
        ftp_logger.setLevel(logging.INFO)

        # Create a file handler
        os.makedirs('logs/ftp/', exist_ok=True)
        handler = logging.FileHandler('logs/ftp/'+datetime.now().strftime("%Y-%m-%d")+'.log')

        # Create a formatter and add it to the handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # Add the handler to the logger
        ftp_logger.addHandler(handler)

        FTP_Enabled = jmod.getvalue(
            key='FTP_Enabled',
            json_dir='settings.json',
            default=True,
            dt=app_settings
        )
        if not bypass_enabled:
            if not FTP_Enabled:
                print("--FTP ACTIVATION WAS ATTEMPTED, BUT WAS CANCELLED AS IT IS DISABLED--", flush=True)
                return

        if use_ssl:
            # Paths to the certificate and key files
            certfile = 'library/ssl/certificate.pem' if certfile is None else certfile
            keyfile = 'library/ssl/private.key' if prvkeyfile is None else prvkeyfile
            os.makedirs("library/ssl/", exist_ok=True)

        class CustomHandler(logging.Handler):
            """
            A custom logging handler that logs messages to a file or prints them to the console based on the 'ftpLogToFile' setting.

            Attributes:
                None

            Methods:
                emit(record): Overrides the emit method of the logging.Handler class to handle the logging of messages.
            """

            def emit(self, record):
                """
                Logs the formatted message to a file or prints it to the console based on the 'ftpLogToFile' setting.

                Args:
                    record (logging.LogRecord): The log record to be emitted.

                Returns:
                    None
                """
                # Load settings from a JSON file
                log_to_file = jmod.getvalue(
                    key='ftpLogToFile',
                    json_dir='settings.json',
                    default=True,
                    dt=app_settings
                )

                msg = self.format(record)

                if log_to_file:
                    os.makedirs('logs/ftp/', exist_ok=True)
                    with open('logs/ftp/'+datetime.now().strftime("%Y-%m-%d")+'.log', 'a') as f:
                        f.write(msg + '\n')
                else:
                    print(msg)

        # Set up logging
        handler = CustomHandler()
        logging.basicConfig(level=logging.INFO, handlers=[handler])

        if use_ssl:
            # Generate a self-signed certificate if it doesn't exist
            if not os.path.isfile(certfile) or not os.path.isfile(keyfile):
                key = rsa.generate_private_key(
                    public_exponent=65537,
                    key_size=2048,
                )

                name = x509.Name([
                    x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
                ])

                cert = x509.CertificateBuilder().subject_name(
                    name
                ).issuer_name(
                    name
                ).public_key(
                    key.public_key()
                ).serial_number(
                    x509.random_serial_number()
                ).not_valid_before(
                    datetime.utcnow()
                ).not_valid_after(
                    datetime.utcnow() + timedelta(days=365)
                ).sign(key, hashes.SHA256())

                # Write our certificate out to disk.
                with open(certfile, "wb") as f:
                    f.write(cert.public_bytes(serialization.Encoding.PEM))

                # Write our key out to disk
                with open(keyfile, "wb") as f:
                    f.write(key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.TraditionalOpenSSL,
                        encryption_algorithm=serialization.NoEncryption(),
                    ))

        root_password = jmod.getvalue(
            key='ftpRootPassword',
            json_dir='settings.json',
            default='password',
            dt=app_settings
        )

        authorizer = DummyAuthorizer()
        authorizer.add_user("root", root_password, ".", perm="elradfmw")
        # Expecting a list of dicts with the following keys: username, password, ftp_homedir, perm
        user_list = jmod.getvalue(
            key='pyhost_users',
            json_dir='settings.json',
            default=[],
            dt=app_settings
        )
        for user in user_list:
            if user['ftp_permissions'] == None:
                # Defaults rights to all
                user['ftp_permissions'] = "elradfmw"

            authorizer.add_user(user['username'], user['password'], user['ftp_homedir'], perm=user['ftp_permissions'])

        # I would make a function which updates the user_list on each new connection
        # (so that the auth table is up-to-date with the json file)
        # But unfortunately, I keep encountering stops when I try to do that.
        # If anyone knows how to do this, please feel free to put in a pull request or issue or something.

        ftpAnonAllowed = jmod.getvalue(
            key='ftpAnonAllowed',
            json_dir='settings.json',
            default=False,
            dt=app_settings
        )
        if ftpAnonAllowed:
            authorizer.add_anonymous(".", perm="elr")

        class MyFTPHandler(FTPHandler):
            """
            Custom FTP handler class that extends the FTPHandler class.

            Attributes:
                None

            Methods:
                on_connect(): Method called when a client connects to the FTP server. It logs the IP address, port, and whether the connection is secure.
            """

            def on_connect(self):
                """
                Method called when a client connects to the FTP server.

                It logs the IP address, port, and whether the connection is secure.
                """
                is_secure = self.ssl_context is not None
                # Gets which account is logging in and sets it in the json file
                for user in user_list:
                    if user['username'] == self.username:
                        user['ftp_connected'] = True
                        break
                logging.info(f"IP \"{self.remote_ip}\" has connected on Port \"{self.remote_port}\". Secure: {is_secure}")

        handler = MyFTPHandler
        handler.authorizer = authorizer

        if use_ssl:
            # Create an SSL context and assign it to the handler
            ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_context.load_cert_chain(certfile=certfile, keyfile=keyfile)
            handler.ssl_context = ssl_context

            handler.tls_control_required = True  # Require TLS for control connection
            handler.tls_data_required = True  # Require TLS for data connection

        if server_port is None:
            server_port = jmod.getvalue(
                key='FtpPort',
                json_dir='settings.json',
                default=789,
                dt=app_settings
            )
        server = ThreadedFTPServer(("localhost", server_port), handler)
        print(f"--FILE TRANSFER PROTOCAL {"SECURED" if use_ssl else ""} RUNNING ON \"localhost:{server_port}\" WITH {len(user_list)} USERS--", flush=True)
        
        try:
            while True:
                server.serve_forever(blocking=False)
                # Updates user list
                user_list = jmod.getvalue(
                    key='pyhost_users',
                    json_dir='settings.json',
                    dt=app_settings
                )

                for user in list(authorizer.user_table.keys()):  # Create a list of keys
                    if user != "root":
                        if user not in user_list:
                            authorizer.remove_user(user)

                for user in user_list:
                    if user not in list(authorizer.user_table.keys()):  # Create a list of keys
                        authorizer.add_user(user['username'], user['password'], user['ftp_homedir'], perm=user['ftp_permissions'])
                    
        except KeyboardInterrupt:
            server.close_all()
            print("--FILE TRANSFER PROTOCAL HAS BEEN STOPPED--")

    def stop():
        ftppid = jmod.getvalue(
            key='ftppid',
            json_dir='settings.json',
            default=None,
            dt=app_settings
        )

        try:
            # Tries built-in method first
            children = multiprocessing.active_children()
            for child in children:
                if child.pid == ftppid:
                    child.terminate()
                    break
        except:
            # Tries my implemented method
            try:
                os.kill(ftppid, 2) # Graceful shutdown
            except:
                try:
                    os.kill(ftppid, 9) # Force shutdown
                except:
                    print("--FTP SERVER COULD NOT BE STOPPED--")

        jmod.setvalue(
            key='ftppid',
            value=None,
            json_dir='settings.json',
            dt=app_settings
        )
        print("--FILE TRANSFER PROTOCAL SERVICE HAS BEEN STOPPED--")

    def enter():
        '''
        This function is used to enter the FTP server's CLI.
        '''
        os.system('cls' if os.name == 'nt' else 'clear')
        # Expects a list of dicts with the following keys: username, password, ftp_homedir, ftp_permissions, ftp_connected
        ftp_userList = jmod.getvalue(
            key='pyhost_users',
            json_dir='settings.json',
            default=[],
            dt=app_settings
        )
        # Gets how many have "ftp_connected" as True
        connected_users = 0
        for user in ftp_userList:
            if user['ftp_connected']:
                connected_users += 1

        # Prints running status
        running = jmod.getvalue(key='ftppid', json_dir='settings.json', default=None, dt=app_settings)
        running_msg = 'running' if running != None else 'not running'
        print(f"FTP server is currently {running_msg}.")

        # Prints how many users are ftp_connected
        if running:
            print(f"{connected_users}/{len(ftp_userList)} users are currently connected.")

        # Prints the FTP server's port
        FtpPort = jmod.getvalue(key='FtpPort', json_dir='settings.json', default=789, dt=app_settings)
        print(f"FTP server is {running_msg} {"on port " if running else ""}{FtpPort if running else f"but is assigned to port {FtpPort}"}.")

        print("Use command 'root' to view the root user's connection details.")

        # Prints various settings's values
        print(f"\nAnonymous login is currently {f'{colours['green']}enabled{colours['white']}' if jmod.getvalue(
            key='ftpAnonAllowed', json_dir='settings.json', default=False, dt=app_settings
            ) else f'{colours['red']}disabled{colours['white']}'}.") # Anonymous login
        print(f"Auto startup is currently {f'{colours['green']}enabled{colours['white']}' if jmod.getvalue(
            key='FTP_Enabled', json_dir='settings.json', default=True, dt=app_settings
            ) else f'{colours['red']}disabled{colours['white']}'}.")

        print("\nWelcome to the FTP server CLI. Type \"help\" for a list of commands.")
        while True:
            command = input(f"{colours['red'] if not running else colours['green']}ftp{colours['reset']}> ").lower()
            if command == "help":
                print("help: Displays this help message.")
                print("exit: Exits the FTP server CLI.")
                print("start: Starts the FTP server.")
                print("stop: Stops the FTP server.")
                print("autoboot: Toggle auto startup on/off.")
                print("port: Changes the port the FTP server runs on.")
                print("anonymous: Toggle anonymous login on/off.")
                print("RPassword: Changes the root password.")
                print("root: Displays the root user's connection details.")
                print("list: Lists all users.")
                print("add: Adds a user.")
                print("remove: Removes a user.")
                print("edit: Edits a user.")
            elif command == "exit":
                print("Exiting the FTP server CLI.")
                break
            elif command == "cls":
                os.system('cls' if os.name == "nt" else 'clear')
            elif command == "start":
                multiprocessing.Process(target=ftp.start, args=(None, None)).start()
            elif command == "stop":
                ftp.stop()
            elif command == "autoboot":
                ftp.autoboot()
            elif command == "list":
                print("Users:")
                ftp.list_users()
            elif command == "add":
                ftp.add_user()
            elif command == "remove":
                ftp.remove_user()
            elif command == "edit":
                print("This command is not yet implemented.")
                # ftp.edit_user()
            elif command == "port":
                ftp.change_port()
            elif command == "anonymous":
                ftp.toggle_anonymous()
            elif command == "RPassword":
                ftp.change_root_password()
            elif command == "root":
                while True:
                    print("Are you sure you want to show the Root Details?")
                    print(f"You should treat these as passwords, and {colours['red']}NEVER{colours['white']} reveal them.\n")
                    answer = input("That being said, Reveal details? (Y/N)\n>>> ").upper()

                    if answer == "Y":
                        answer = True
                    elif answer == "N":
                        answer = False
                        print("Cancelled.")
                        return False
                    else:
                        print("Invalid answer! Y or N only")
                        continue 
                    break
                
                print("USERNAME: root")
                print(f"ROOT PASSWORD: {jmod.getvalue(key="ftpRootPassword", json_dir="settings.json")}")
            else:
                print("Invalid command.")

    def change_port():
        '''
        This function is used to change the port the FTP server runs on.
        '''
        from .application import application
        new_port = application.datareqs.get_port()
        del application

        jmod.setvalue(
            key='FtpPort',
            value=int(new_port),
            json_dir='settings.json',
            dt=app_settings
        )

        print(f"Port has been changed to {new_port}.")
        

    def toggle_anonymous():
        '''
        This function is used to toggle anonymous login on/off.
        '''
        # Load settings from a JSON file
        ftpAnonAllowed = jmod.getvalue(
            key='ftpAnonAllowed',
            json_dir='settings.json',
            default=False,
            dt=app_settings
        )

        if ftpAnonAllowed:
            jmod.setvalue(
                key='ftpAnonAllowed',
                value=False,
                json_dir='settings.json',
                dt=app_settings
            )
            print("Anonymous login has been disabled.")
        else:
            jmod.setvalue(
                key='ftpAnonAllowed',
                value=True,
                json_dir='settings.json',
                dt=app_settings
            )
            print("Anonymous login has been enabled.")

    def change_root_password():
        '''
        This function is used to change the root password.
        '''
        while True:
            new_password = input("New password: ")
            if new_password == "":
                print("Password cannot be blank.")
                continue
            elif new_password.isalnum() == False:
                print("Password must be alphanumeric.")
                continue
            elif len(new_password) < 4:
                print("Password must be at least 4 characters long.")
                continue
            else:
                break

        jmod.setvalue(
            key='ftpRootPassword',
            value=new_password,
            json_dir='settings.json',
            dt=app_settings
        )

        print("Root password has been changed.")

    def autoboot():
        '''
        This function is used to toggle auto startup on/off.
        '''
        # Load settings from a JSON file
        FTP_Enabled = jmod.getvalue(
            key='FTP_Enabled',
            json_dir='settings.json',
            default=True,
            dt=app_settings
        )

        if FTP_Enabled:
            jmod.setvalue(
                key='do_autostart',
                value=False,
                json_dir='settings.json',
                dt=app_settings
            )
            print("FTP Auto startup has been disabled.")
        else:
            jmod.addvalue(
                key='FTP_Enabled',
                value=True,
                json_dir='settings.json',
                dt=app_settings
            )
            print("FTP Auto startup has been enabled.")

    def add_user():
        '''
        This function is used to add a user to the FTP server.
        '''
        # Load settings from a JSON file
        ftp_userList = jmod.getvalue(
            key='pyhost_users',
            json_dir='settings.json',
            default=[],
            dt=app_settings
        )

        # Get the username
        while True:
            username = input("Username: ")
            if username == "":
                print("Username cannot be blank.")
                continue
            elif username.isalnum() == False:
                print("Username must be alphanumeric.")
                continue
            elif username in ftp_userList:
                print("Username already exists.")
                continue
            else:
                break

        new_user['username'] = username

        # Get the password
        while True:
            password = input("Password: ")
            if password == "":
                print("Password cannot be blank.")
                continue
            elif password.isalnum() == False:
                print("Password must be alphanumeric.")
                continue
            elif len(password) < 4:
                print("Password must be at least 4 characters long.")
                continue
            else:
                break
            
        new_user['password'] = password

        # Get the ftp_homedir
        while True:
            instances = os.listdir("instances/")
            print("\nPlease select an app for the user to have access to.")
            for instance in instances:
                print(instance)
                print(f"{colours['gray']}{jmod.getvalue(key='description', json_dir=f'instances/{instance}/config.json', default='No description provided.')}{colours['reset']}")

            homedir_app = input("\nLock to app: ")
            if homedir_app not in homedir_app:
                print("App does not exist.")
                continue
            break

        while True:
            # Asks if the user should be locked to content
            lock_to_content = input("Lock to content folder only? (y/n): ")
            if lock_to_content == "y":
                new_user['ftp_homedir'] = f"instances/{homedir_app}/content"
                print(f"User will be locked to the content folder of the \"{homedir_app}\" app.")
                break
            else:
                new_user['ftp_homedir'] = f"instances/{homedir_app}"
                print(f"User will be locked to the \"{homedir_app}\" app.")
                break

        # Get the ftp_permissions
        while True:
            # Asks the user if they want to use 1 of 3 presets or custom
            preset = input("Would you like to use a preset? (y/n): ")
            if preset == "y":
                # Asks the user which preset they want to use
                preset = input("Which preset would you like to use?\n1. Read\n2. Read and Write\n>>> ")
                if preset == "1":
                    new_user['ftp_permissions'] = "elr"
                    break
                elif preset == "2":
                    new_user['ftp_permissions'] = "elradfmw"
                    break
                else:
                    print("Invalid preset.")
                    continue
            elif preset == "n":
                # Asks the user for custom ftp_permissions
                while True:
                    perm = input("ftp_permissions (elradfmwM): ")
                    if perm == "":
                        print("ftp_permissions cannot be blank.")
                        continue
                    elif perm.isalnum() == False:
                        print("ftp_permissions must be alphanumeric.")
                        continue
                    else:
                        new_user['ftp_permissions'] = perm
                        break
                break
            else:
                print("Invalid input.")
                continue

        

        # Save the list to a JSON file
        jmod.addvalue(
            key='pyhost_users',
            value=new_user,
            json_dir='settings.json',
            dt=app_settings
        )

        print(f"User \"{username}\" has been added.")

    def remove_user():
        '''
        This function is used to remove a user from the FTP server.
        '''
        # Load settings from a JSON file
        ftp_userList = jmod.getvalue(
            key='pyhost_users',
            json_dir='settings.json',
            default=[],
            dt=app_settings
        )

        # Get the username
        while True:
            username = input("Username: ")
            if username == "":
                print("Username cannot be blank.")
                continue
            elif username.isalnum() == False:
                print("Username must be alphanumeric.")
                continue
            elif username not in ftp_userList:
                print("Username does not exist.")
                continue
            else:
                break

        # Remove the user from the list
        for user in ftp_userList:
            if user['username'] == username:
                ftp_userList.remove(user)

        # Save the list to a JSON file
        jmod.addvalue(
            key='pyhost_users',
            value=ftp_userList,
            json_dir='settings.json',
            dt=app_settings
        )

        print(f"User \"{username}\" has been removed.")

    def list_users():
        ftp_userList = jmod.getvalue(
            key='pyhost_users',
            json_dir='settings.json',
            default=[],
            dt=app_settings
        )
        if len(ftp_userList) >= 1:
            colour = True
            print("====================")
            for user in ftp_userList:
                if user['ftp_permissions'] == "r":
                    user['ftp_permissions'] == "Read Only" # Only a visual effect as it doesn't save
                elif user['ftp_permissions'] == "rw":
                    user['ftp_permissions'] = "Read and Write"

                if colour:
                    print(f"Username: {user['username']}\nPassword: {user['password']}\nHomedir: {user['ftp_homedir']}\nPermissions: {user['ftp_permissions']}\n====================\n")
                else:
                    print(f"\033[1;37;40mUsername: {user['username']}\nPassword: {user['password']}\nHomedir: {user['ftp_homedir']}\nPermissions: {user['ftp_permissions']}\n====================\n")
                colour = not colour # Switches the colour
        else:
            print("There are no users.")
