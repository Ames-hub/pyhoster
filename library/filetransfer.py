import time
import os
import ssl
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
try:
    from .jmod import jmod
    from .data_tables import app_settings
    from .userman import userman
except ImportError as err:
    print("Hello! To run Pyhost, you must run the file pyhost.py located in this projects root directory, not this file.\nThank you!")
    from library.pylog import pylog
    pylog().error(f"Import error in {__name__}", err)

from .pylog import pylog
pylogger = pylog()

def generate_ssl(certfile_dir, keyfile_dir, hostname="localhost"):
    # Generate a self-signed certificate if it doesn't exist
    if not os.path.isfile(certfile_dir) or not os.path.isfile(keyfile_dir):
        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        name = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u"{}".format(hostname)),
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
        with open(certfile_dir, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))

        # Write our key out to disk
        with open(keyfile_dir, "wb") as f:
            f.write(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            ))

colours = {
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

def get_username():
    while True:
        print("<--FTP PERMISSIONS MENU-->\n")
        print("Type \"exit\" to exit.\n")
        userman.list_users()
        username = input("Please select a user: ")
        if not userman.check_exists(username):
            print("User does not exist.")
            continue

        print(f"Selected user: {username}")
        correct = input("Is this right? (Y/N) | ")
        if correct.lower() == "y":
            break
        elif correct.lower() == "n":
            username = None
            continue
        else:
            print("Invalid answer.")
            continue
    return username

class ftp:
    def start(certfile=None, prvkeyfile=None, server_port=None, use_ssl=True, bypass_enabled=False):
        # Create a logger
        ftp_logger = pylog(filename='logs/ftp/%TIMENOW%.log')

        FTP_Enabled = jmod.getvalue(
            key='FTP_Enabled',
            json_dir='settings.json',
            default=True,
            dt=app_settings
        )
        if not bypass_enabled:
            if not FTP_Enabled:
                print("<--FTP ACTIVATION WAS ATTEMPTED, BUT WAS CANCELLED AS IT IS DISABLED-->", flush=True)
                return
            
        # mark self as online
        jmod.setvalue(
            key='ftppid',
            value=os.getpid(),
            json_dir='settings.json',
            dt=app_settings
        )

        if use_ssl:
            # Paths to the certificate and key files
            certfile = 'library/ssl/certificate.pem' if certfile is None else certfile
            keyfile = 'library/ssl/private.key' if prvkeyfile is None else prvkeyfile
            ssl_exist = {
                "prv": os.path.isfile(certfile),
                "cert": os.path.isfile(certfile),
                }
            os.makedirs("library/ssl/", exist_ok=True)
            if not ssl_exist["prv"] or not ssl_exist["cert"]:
                generate_ssl(certfile, keyfile)

        root_password = jmod.getvalue(
            key='ftpRootPassword',
            json_dir='settings.json',
            default='password',
            dt=app_settings
        )

        authorizer = DummyAuthorizer()
        authorizer.add_user("root", root_password, homedir=".", perm="elradfmw")
        # Expecting a list of dicts with the following keys: username, password, ftp_dirs, perm
        user_list = jmod.getvalue(
            key='pyhost_users',
            json_dir='settings.json',
            default={},
            dt=app_settings
        )
        for user in user_list:
            user = user_list[user]
            if user['ftp_permissions'] == None:
                # Defaults rights to all
                user['ftp_permissions'] = "elradfmw"

            for app_name in dict(user['ftp_dirs']).keys():
                authorizer.add_user(f"{user['username']}:{app_name}", user['password'], user['ftp_dirs'][app_name], perm=user['ftp_permissions'])

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

        connected_users = []
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
                ftp_logger.info(f"IP \"{self.remote_ip}\" with username \"{self.username}\" has connected on Port \"{self.remote_port}\". Secure: {is_secure}")

            def on_login(self, username):
                connected_users.append(username)

            def on_logout(self, username): # Does not count on disconnect. gotta time them out
                connected_users.remove(username)

            def get_connected_users(cls):
                return list(connected_users)

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
                default=4035,
                dt=app_settings
            )
        server = ThreadedFTPServer(("localhost", server_port), handler)
        print(f"<--FILE TRANSFER PROTOCAL {'SECURED' if use_ssl else ''} RUNNING ON \"localhost:{server_port}\" WITH {len(user_list)} USERS-->", flush=True)

        counter = 0
        try:
            while True:
                server.serve_forever(blocking=False)
                # Updates user list
                user_list = jmod.getvalue(
                    key='pyhost_users',
                    json_dir='settings.json',
                    dt=app_settings
                )
                if len(user_list) > 100:
                    # Only updates every 50 loop-throughs to save on resources for people with lots of users
                    if counter & 50 + int((len(user_list) // 2)) == 0:
                        pass

                # TODO: Find a way to remove users not in user_list from the authorizer and add new users

                # Marks users as not connected or connected
                for user in user_list:
                    user = user_list[user]
                    for conn_user in connected_users:
                        conn_user: str
                        if conn_user.split(":")[0] == user['username']:
                            jmod.setvalue(
                                key=f"pyhost_users.{user['username']}.ftp_connected",
                                value=True,
                                json_dir='settings.json',
                                dt=app_settings
                            )
                        else:
                            jmod.setvalue(
                                key=f"pyhost_users.{user['username']}.ftp_connected",
                                value=False,
                                json_dir='settings.json',
                                dt=app_settings
                            )

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
        print("\nWelcome to the FTP server CLI. Type \"help\" for a list of commands.")
        from .userman import userman
        while True:
            # Expects a list of dicts with the following keys: username, password, ftp_dirs, ftp_permissions, ftp_connected
            ftp_userList = jmod.getvalue(
                key='pyhost_users',
                json_dir='settings.json',
                default=[],
                dt=app_settings
            )
            # Gets how many have "ftp_connected" as True
            connected_users = 0
            for user in ftp_userList:
                user = ftp_userList[user]
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
            FtpPort = jmod.getvalue(key='FtpPort', json_dir='settings.json', default=4035, dt=app_settings)
            print(f"FTP server is {running_msg} {'on port ' if running else ''}{FtpPort if running else f'but is assigned to port {FtpPort}'}.")

            print("Use command 'root' to view the root user's connection details.")
            # Prints various settings's values
            anon_allowed = jmod.getvalue(key='ftpAnonAllowed', json_dir='settings.json', default=False, dt=app_settings)
            anon_login_msg = colours['green'] + "enabled" + colours['white'] if anon_allowed else colours['red'] + "disabled" + colours['white']
            print(f"\nAnonymous login is currently {anon_login_msg}.") # Anonymous login

            ftp_autostart = jmod.getvalue(key='FTP_Enabled', json_dir='settings.json', default=True, dt=app_settings)
            auto_start_msg = colours['green'] + "enabled" + colours['white'] if ftp_autostart else colours['red'] + "disabled" + colours['white']
            print(f"Auto startup is currently {auto_start_msg}")

            command = input(f"{colours['red'] if not running else colours['green']}ftp{colours['white']}> ").lower()
            if command == "help":
                print("help: Displays this help message.")
                print("exit: Exits the FTP server CLI.")
                print("start: Starts the FTP server.")
                print("stop: Stops the FTP server.")
                print("autoboot: Toggle auto startup on/off.")
                print("port: Changes the port the FTP server runs on.")
                print("anonlogin: Toggle anonymous login on/off.")
                print("RPassword: Changes the root password.")
                print("root: Displays the root user's connection details.")
                print("perms: Enters the FTP Permissions Menu.")
                print("port: Changes the port the FTP server runs on.")
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
                multiprocessing.Process(target=ftp.start, args=(), kwargs={"bypass_enabled": True}).start()
                time.sleep(0.5)
            elif command == "stop":
                ftp.stop()
            elif command == "autoboot":
                ftp.autoboot()
            elif command == "list":
                print("Users:")
                userman.list_users()
            elif command == "add":
                userman.add_user()
            elif command == "remove":
                userman.remove_user()
            elif command == "port":
                ftp.change_port()
            elif command == "edit":
                print("This command is not yet implemented.")
                # ftp.edit_user()
            elif command == "port":
                ftp.change_port()
            elif command == "anonlogin":
                ftp.toggle_anonymous()
            elif command == "perms":
                ftp_perms.modify_perms()
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
                print(f"ROOT PASSWORD: {jmod.getvalue(key='ftpRootPassword', json_dir='settings.json')}")
            elif command == "":
                continue # Catches blank input as sometimes a 'input' line is printed over and the user pressed enter to dismiss it 
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
            jmod.setvalue(
                key='FTP_Enabled',
                value=True,
                json_dir='settings.json',
                dt=app_settings
            )
            print("FTP Auto startup has been enabled.")

class ftp_perms:
    def enter():
        while True:
            print("<--FTP PERMISSIONS MENU-->\n")
            print("Type \"help\" for a list of commands.")
            cmd = input(f"{colours['cyan']}ftp permission man> ").lower()

            if cmd == "help":
                ftp_perms.help_msg()
            elif cmd == "exit":
                print("Exiting FTP Permissions Menu.")
                break
            elif cmd == "cls":
                from .application import application # Importing here to prevent circular import should they happen
                application.clear_console()
                del application
            elif cmd == "list":
                print("Users:")
                userman.list_users()
            elif cmd == "userperm":
                ftp_perms.modify_perms()
            else:
                print("Invalid command.")
                time.sleep(3)

    def help_msg():
        print("help: Displays this help message.")
        print("exit: Exits the FTP Permissions Menu.")
        print("cls: Clears the console.")
        print("list: Lists all users.")
        print("userperm: Selects a user to modify permissions of.")

    def modify_perms(username=None):
        username = get_username()
        user = userman.user(username)
        while True:
            perms = user.json['ftp_permissions']
            pm = ""
            if "e" in perms:
                pm += "(e) Change Directories\n"
            if "l" in perms:
                pm += "(l) List Files\n"
            if "r" in perms:
                pm += "(r) Retrieve Files\n"
            if "a" in perms:
                pm += "(a) Append Files\n"
            if "d" in perms:
                pm += "(d) Delete Files\n"
            if "f" in perms:
                pm += "(f) Rename Files\n"
            if "m" in perms:
                pm += "(m) Make Directories\n"
            if "w" in perms:
                pm += "(w) Store Files\n"
            if "M" in perms:
                pm += "(M) Change file permission\n"
            if "T" in perms:
                pm += "(T) Change known file Modification time\n"

            print(f"\n{colours['yellow']}READ THE DOCS: https://pyftpdlib.readthedocs.io/en/latest/api.html{colours['white']}")
            print(f"Selected user: {username}")
            print(pm)
            print("The user can do the above.")
            new_permissions = input("New Permissions: ")
            if new_permissions == "help":
                # Prints all possible permissions and what they do
                print("Enter these by letter to choose which permissions the user has.")
                print("e: Change Directories")
                print("l: List Files")
                print("r: Retrieve Files")
                print("a: Append Files")
                print("d: Delete Files")
                print("f: Rename Files")
                print("m: Make Directories")
                print("w: Store Files")
                print("M: Change file permission")
                print("T: Change known file Modification time")
                input("Press enter to continue.")
            elif new_permissions == "exit":
                return False
            else:
                # Checks if the user has entered valid permissions
                valid_perms = "elradfmwMT"
                for perm in new_permissions:
                    if perm not in valid_perms:
                        print(f"Invalid permission: {perm}")
                        continue
                break

        jmod.setvalue(
            key=f"pyhost_users.{username}.ftp_permissions",
            value=new_permissions,
            json_dir='settings.json',
            dt=app_settings
        )
        print(f"{colours['green']}Permissions for {username} have been changed to {new_permissions}.{colours['white']}\n")