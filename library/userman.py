import os
from .jmod import jmod
import uuid, datetime, multiprocessing
import logging
from .data_tables import new_user, app_settings

colours = {
    'reset': "\033[0;37;40m",
    'gray': "\033[1;30;40m",
    'red': "\033[1;31;40m",
    'green': "\033[1;32;40m",
    'yellow': "\033[1;33;40m",
    'blue': "\033[1;34;40m",
    'magenta': "\033[1;35;40m",
    'cyan': "\033[1;36;40m",
    'white': "\033[1;37;40m"
}

valid_sessions = {}

# Manages the valid sessions
def token_manager():
    try:
        while True:
            for session in valid_sessions:
                # Deletes the session if it is older than 12 hours
                # TODO: Make timeout configurable
                if datetime.datetime.now().date() - valid_sessions[session][0] >= datetime.timedelta(hours=12):
                    del valid_sessions[session]
    except KeyboardInterrupt:
        return True

if __name__ == "__main__":
    token_man = multiprocessing.Process(
        target=token_manager,
        args=()
    )
    jmod.setvalue(
        key='api.tokenManPid',
        value=token_man.pid,
        json_dir='settings.json',
        dt=app_settings
    )
    token_man.start()
    logging.info("Token manager has started.")

class userman:
    def enter():
        while True:
            try:
                cmd = input(f"{colours['green']}UserMan{colours['reset']}> ")
                if cmd == "add":
                    userman.add_user()
                    continue
                elif cmd == "remove":
                    userman.remove_user()
                    continue
                elif cmd == "list":
                    userman.list_users()
                    continue
                elif cmd == "exit":
                    return True
                elif cmd == "help":
                    userman.help()
                elif cmd == "lock":
                    userman.lock()
                    continue
                elif cmd == "unlock":
                    userman.unlock()
                    continue
                else:
                    print("Invalid command.")
                    continue
            except AssertionError as err:
                print(str(err))
                continue

    def help():
        print(f"{colours['green']}UserMan{colours['reset']} is a tool for managing users for the FTP server.")
        print("Commands:")
        cmds = {
            "add": "Add a user.",
            "remove": "Remove a user.",
            "help": "Show this help message.",
            "list": "List all users.",
            "lock": "Lock a user.",
            "unlock": "Unlock a user.",
            "exit": "Exit UserMan.",
        }
        for cmd in cmds:
            print(f"{colours['green']}{cmd}{colours['reset']}: {cmds[cmd]}")

    def lock(username=None):
        if username is None:
            while True:
                username = input("Username: ")
                if username == "":
                    print("Username cannot be blank.")
                    continue
                elif username.isalnum() == False:
                    print("Username must be alphanumeric.")
                    continue
                elif userman.check_exists(username) == False:
                    print("Username does not exist.")
                    continue
                else:
                    break

        jmod.setvalue(
            key=f'pyhost_users.{username}.locked',
            value=True,
            json_dir='settings.json',
            dt=app_settings
        )
        print(f"User \"{username}\" has been locked.")

    def unlock(username=None):
        if username is None:
            while True:
                username = input("Username: ")
                if username == "":
                    print("Username cannot be blank.")
                    continue
                elif username.isalnum() == False:
                    print("Username must be alphanumeric.")
                    continue
                elif userman.check_exists(username) == False:
                    print("Username does not exist.")
                    continue
                else:
                    break

        jmod.setvalue(
            key=f'pyhost_users.{username}.locked',
            value=False,
            json_dir='settings.json',
            dt=app_settings
        )
        print(f"User \"{username}\" has been unlocked.")

    def add_user():
        '''
        This function is used to add a user to the FTP server.
        '''
        # Load settings from a JSON file
        UserList = jmod.getvalue(
            key='pyhost_users',
            json_dir='settings.json',
            default={},
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
            elif username in UserList:
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

        # asks the user if they want to handle ftp
        while True:
            handle_ftp = input("Do you want to setup this user for FTP? (y/n): ")
            if handle_ftp == "y":
                handle_ftp = True
                break
            elif handle_ftp == "n":
                handle_ftp = False
                break
            else:
                print("Invalid input.")
                continue
        # Get the ftp_dirs
        if handle_ftp:
            accepted_directories = {}
            while True:
                instances = os.listdir("instances/")
                print("\nPlease select an app for the user to have access to.")
                print("Type 'done' or 'cancel' to finish.\n")
                for instance in instances:
                    if instance not in accepted_directories.keys():
                        print(instance)
                        print(f"{colours['gray']}{jmod.getvalue(key='description', json_dir=f'instances/{instance}/config.json', default='No description provided.')}{colours['reset']}")

                app_choice = input("\nLock to app: ")
                if app_choice in ["done", "cancel"]:
                    print(f"Done selecting {len(accepted_directories.keys())} apps.")
                    print("===============================")
                    for app in accepted_directories.keys():
                        print(f"{app}: {accepted_directories[app]}")
                    print("===============================")
                    break
                elif app_choice not in os.listdir("instances/"):
                    print("App does not exist.")
                    continue
                elif app_choice in accepted_directories.keys():
                    print("App already selected.")
                    continue

                while True:
                    # Asks if the user should be locked to content
                    lock_to_content = input("Lock to content folder only? (y/n): ")
                    if lock_to_content == "y":
                        new_user['ftp_dirs'] = f"instances/{app_choice}/content"
                        print(f"User will be locked to the content folder of the \"{app_choice}\" app.")
                        break
                    else:
                        new_user['ftp_dirs'] = f"instances/{app_choice}"
                        print(f"User will be locked to the \"{app_choice}\" app.")
                        break

                accepted_directories.update({app_choice: new_user['ftp_dirs']})
                add_another = False
                while True:
                    cont = input("Add another app? (y/n): ")
                    if cont == "y":
                        add_another = True
                        break
                    else:
                        add_another = False
                        break

                if add_another:
                    continue
                else:
                    new_user['ftp_dirs'] = accepted_directories
                    break

        # Get the ftp_permissions
        while True:
            # Asks the user if they want to use 1 of 3 presets or custom
            preset = input("We need to handle user FTP permissions.\nWould you like to use a preset? (y/n): ")
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

        # Asks if the user wants to handle setting up their access to the API
        while True:
            handle_api = input("Do you want to setup this user for the API? (y/n): ")
            if handle_api == "y":
                handle_api = True
                break
            elif handle_api == "n":
                handle_api = False
                break
            else:
                print("Invalid input.")
                continue

        if handle_api:
            while True:
                # Gets the API permissions
                print("Please select the API permissions for this user.")
                print("Do you want to use a template/preset or custom?")
                print("1. Template/preset\n2. Custom")
                choice = input(">>> ")
                if choice == "1":
                    # Asks the user which preset they want to use
                    preset = input("Which preset would you like to use?\n1. Read\n2. Read and Write\n>>> ")
                    if preset == "1":
                        new_user['api_permissions'] = "r"
                        break
                    elif preset == "2":
                        new_user['api_permissions'] = "rw"
                        break
                    else:
                        print("Invalid preset.")
                        continue


        # Asks if the user should be locked
        while True:
            lock = input("Should we start their account as locked? (y/n): ")
            if lock == "y":
                new_user['locked'] = True
                break
            elif lock == "n":
                new_user['locked'] = False
                break
            else:
                print("Invalid input.")
                continue

        UserList = dict(UserList)
        UserList[username] = new_user

        # Save the list to a JSON file
        jmod.setvalue(
            key='pyhost_users',
            value=UserList,
            json_dir='settings.json',
            dt=app_settings
        )

        print(f"User \"{username}\" has been added.")

    def check_exists(username):
        '''
        This function is used to check if a user exists.
        '''
        # Load settings from a JSON file
        UserList = jmod.getvalue(
            key='pyhost_users',
            json_dir='settings.json',
            default={},
            dt=app_settings
        )

        # Check if the user exists
        for user in UserList:
            if user == username:
                return True
        return False

    def remove_user():
        '''
        This function is used to remove a user from the FTP server.
        '''
        # Load settings from a JSON file
        UserList = jmod.getvalue(
            key='pyhost_users',
            json_dir='settings.json',
            default={},
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
            elif userman.check_exists(username) == False:
                print("Username does not exist.")
                continue
            else:
                break
        
        # Removes key "username" and its content
        del UserList[username]

        # Save the list to a JSON file
        jmod.setvalue(
            key='pyhost_users',
            value=UserList,
            json_dir='settings.json',
            dt=app_settings
        )

        print(f"User \"{username}\" has been removed.")

    def list_users(for_CLI=True):
        UserList = jmod.getvalue(
            key='pyhost_users',
            json_dir='settings.json',
            default={},
            dt=app_settings
        )
        if for_CLI:
            if len(UserList) >= 1:
                colour = True
                print("====================")
                for user in UserList:
                    if user['ftp_permissions'] == "r":
                        user['ftp_permissions'] == "Read Only" # Only a visual effect as it doesn't save
                    elif user['ftp_permissions'] == "rw":
                        user['ftp_permissions'] = "Read and Write"

                    if colour:
                        print(f"Username: {user['username']}\nPassword: {user['password']}\nHomedir: {user['ftp_dirs']}\nPermissions: {user['ftp_permissions']}\n====================\n")
                    else:
                        print(f"\033[1;37;40mUsername: {user['username']}\nPassword: {user['password']}\nHomedir: {user['ftp_dirs']}\nPermissions: {user['ftp_permissions']}\n====================\n")
                    colour = not colour # Switches the colour
            else:
                print("There are no users.")
        else:
            return UserList

    def is_locked(username):
        '''
        This function is used to check if a user account is locked.
        '''
        # Load settings from a JSON file
        UserList = jmod.getvalue(
            key='pyhost_users',
            json_dir='settings.json',
            default={},
            dt=app_settings
        )
        # Check if the user is locked
        user = UserList.get(username, None)
        if user == None:
            raise userman.errors.UserDoesNotExist
        else:
            return dict(user).get('locked', True)

    class user():
        def __init__(self, username) -> None:
            if userman.check_exists(username):
                self.username = username
            else:
                raise userman.errors.UserDoesNotExist(f"User \"{username}\" does not exist.")

        def get_password(self):
            '''
            This function is used to get a user's password.
            '''
            # Load settings from a JSON file
            UserList = jmod.getvalue(
                key='pyhost_users',
                json_dir='settings.json',
                default={},
                dt=app_settings
            )

            # Get the password
            for user in UserList:
                if user == self.username:
                    return UserList[user]['password']
            return False

        def set_password(self, password):
            '''
            This function is used to set a user's password.
            '''
            # Save the list to a JSON file
            return jmod.setvalue(
                key=f'pyhost_users.{self.username}.password',
                value=password,
                json_dir='settings.json',
                dt=app_settings
            )

        def lock(self):
            return userman.lock(self.username)

        def unlock(self):
            return userman.unlock(self.username)
        
        def is_locked(self):
            return userman.is_locked(self.username)
        
        def get_ftp_dirs(self):
            '''
            This function is used to get a user's FTP directories.
            '''
            # Load settings from a JSON file
            UserList = jmod.getvalue(
                key='pyhost_users',
                json_dir='settings.json',
                default={},
                dt=app_settings
            )

            # Get the ftp_dirs
            for user in UserList:
                if user == self.username:
                    return UserList[user]['ftp_dirs']
            return False
        
    class errors:
        # Using this class so I can catch specific things without returning strings 
        class UserDoesNotExist(Exception):
            '''
            This error is raised when a user does not exist.
            '''
            def __init__(self):
                super().__init__("User does not exist.")

        class UserLocked(Exception):
            '''
            This error is raised when a user is locked.
            '''
            def __init__(self):
                super().__init__("User is locked out.")

    class session():
        '''
        This class is used to manage sessions.
        Returns -1 if the user does not exist.
        Returns -2 if the user is locked.

        Returns a session ID if successful.
        '''
        def __init__(self, username, password, IP_Address=None) -> None:
            self.username = username
            self.password = password
            
            nulls = [None, "", " "]

            if username in nulls or password in nulls:
                self.htmlstatus = 401

            # Checks if the user already has a session
            for session in valid_sessions:
                if valid_sessions[session]['username'] == username:
                    self.htmlstatus = 200
                    self.token = session
                    return

            try:
                self.htmlstatus = 200
                if userman.check_exists(username) is False:
                    self.htmlstatus = 401
                else:
                    if not userman.user(username).get_password() == password:
                        self.htmlstatus = 403

                if userman.is_locked(username):
                    self.htmlstatus = 423
            except userman.errors.UserDoesNotExist:
                self.htmlstatus = 401

            if self.htmlstatus == 200:
                self.token = self.make_token(IP=IP_Address)
            else:
                self.token = None

        def get_user(token, return_full=False):
            '''
            This function is used to get the user from a session token.
            '''
            if token in valid_sessions.keys():
                return valid_sessions[token]['username'] if not return_full else valid_sessions[token]
            else:
                return None

        def make_token(self, IP):
            '''
            This function is used to generate a session token.
            '''
            token = uuid.uuid4().hex
            valid_sessions[token] = {
                "start": datetime.datetime.now().date(),
                "username": self.username,
                "IP_Address": IP
                }
            return token
        
        def validate_session(session):
            '''
            This function is used to validate a session.
            '''
            return session in valid_sessions.keys()

    class api:
        def login(username:str, password:str) -> bool:
            '''
            This function is used to login to the API.
            '''
            try:
                username = str(username)
                password = str(password)
            except:
                return False
            # Load user's list from a JSON file
            users = userman.list_users(for_CLI=False)
            if username in users.keys():
                if users[username]['password'] == password:
                    jmod.setvalue(
                        key=f'pyhost_users.{username}.api.logged_in',
                        value=True,
                        json_dir='settings.json',
                        dt=app_settings
                    )
                    return True
                else:
                    return False

        def logout(username):
            jmod.setvalue(
                key=f'pyhost_users.{username}.api.logged_in',
                value=False,
                json_dir='settings.json',
                dt=app_settings
            )
