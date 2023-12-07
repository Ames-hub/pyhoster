import logging, time, os
import uuid
from .jmod import jmod
from .data_tables import app_settings, web_config_dt
import multiprocessing

colours = {
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "purple": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
    "black": "\033[98m",
    "gray": "\033[90m",
}

with open("library/webpages/warden_login.html", "r") as f:
    warden_login = f.read(),

valid_sessions = []

session_timeout = 60 * 60 * 24 # 24 hours
def timeout_sessions():
    '''Timeouts sessions after a certain amount of time.'''
    try:
        while True:
            for session in valid_sessions:
                try:
                    valid_sessions.remove(session)
                except ValueError: # Session already removed
                    pass
            time.sleep(session_timeout)
    except KeyboardInterrupt:
        return
    
if __name__ == "__main__":
    multiprocessing.Process(target=timeout_sessions).start()

class warden:
    def enter(app_name = None):
        '''Enters the warden CLI.'''
        # Prompt for app name if not provided
        # (app name is required, as warden is per-instance)
        if app_name == None:
            # Gets the app name
            app_list = os.listdir("instances/")
            while True:
                print("Please enter the name of the app you want to enter the warden for. (Case sensitive)\nUse 'exit' to exit.")
                # Prints apps
                for app in app_list:
                    print(f" - {app}")
                    desc = jmod.getvalue('description',f'instances/{app}/config.json',dt=web_config_dt,default='No description provided.')
                    print(f"{colours['gray']}{desc}{colours['white']}")
                app_name = input("App Name: ")
                if app_name not in app_list:
                    print("App name valid.")
                    continue
                else:
                    print("App exists. Continuing...")
                    break

        if app_name not in os.listdir("instances/"):
            print("App does not exist.")
            return

        # TODO Complete these commands. only enable, disable, add/rempage, and exit are done.
        commands = [
            "help - Displays this message.",
            "exit - Exits warden.",
            "enable - Enables the warden for the app.",
            "disable - Disables the warden for the app.",
            "status - Displays the status of the warden.",
            "pages - Lists the pages that are protected by the warden.",
            "addpage - Adds a page to the warden.",
            "rempage - Removes a page from the warden.",
            "clearpages - Removes all pages from the warden.",
            "password - Changes the password for pages.",
        ]

        iterance = 1
        valid_cmds = {} # Used to navigate from numbers to valid commands
        for command in commands:
            iterance += 1
            valid_cmds[iterance] = command.split(" ")[0] # Adds the command without the description.
            # Always use the first word of the command as the command name.

        while True:
            # Can't put enabled checker outside loop, variable may change.
            wrdn = dict(jmod.getvalue(
                key="warden",
                json_dir=f"instances/{app_name}/config.json",
                dt=web_config_dt,
                default={}
            ))
            enabled = wrdn.get("enabled")
            pages = wrdn.get("pages")
            timesAccessed = wrdn.get("timesAccessed", "UNKNOWN")
            try:
                print(f"\n{colours['green']}Welcome to the Warden{colours['white']}. Type 'help' for a list of commands.")
                # information about warden's state in the app
                os.system("cls" if os.name == "nt" else "clear")
                print(f"Status for app: {app_name}")
                print(f"WARDEN IS CURRENTLY {"RUNNING." if enabled else "INACTIVE."}")
                print(f"I am currently protecting {len(pages)} pages.")
                print(f"Those pages have been accessed {timesAccessed} times.\n")

                cmd = input(f"{colours['red' if not enabled else 'green']}warden{colours['white']}> ")
            except Exception as err:
                logging.info(err)
                print(str(err))

            if cmd == "help":
                print("Commands listed below...")
                iterance = 1
                for command in commands:
                    print(f"{iterance}. {command}")
                    iterance += 1
                input("Press enter to continue and erase this message...")
                
            elif cmd == "exit":
                print("Exiting warden for \""+str(app_name)+"\"...")
                return True
            elif cmd == "enable":
                warden.set_status(app_name, True)
            elif cmd == "disable":
                warden.set_status(app_name, False)
            elif cmd == "addpage":
                warden.add_page(app_name)
            elif cmd == "rempage":
                warden.rem_page(app_name)
            elif cmd == "list":
                warden.list_all(app_name)
            elif cmd == "clearpages":
                jmod.setvalue(
                    key="warden.pages",
                    json_dir=f"instances/{app_name}/config.json",
                    dt=web_config_dt,
                    value=[]
                )
                print("Pages cleared.")
            elif cmd == "password":
                warden.change_password(app_name)
            elif cmd == "status":
                print(f"Status for app: {app_name}")
                print(f"WARDEN IS CURRENTLY {"RUNNING." if enabled else "INACTIVE."}")
                print(f"I am currently protecting {len(pages)} pages.")
                print(f"Those pages have been accessed {timesAccessed} times.\n")
                input("Press enter to continue and erase this message...")
            else:
                print("Invalid command.")
                time.sleep(2)
    
    def set_status(app_name:str, status:bool=True):
        '''Set the warden's status of protecting for an app.'''
        jmod.setvalue(
            key="warden.enabled",
            json_dir=f"instances/{app_name}/config.json",
            dt=web_config_dt,
            value=status
        )
        print("Warden enabled.")

    def list_all(app_name:str):
        # Uses os.walk to go through every file in the content directory and subdirs and list their directories
        counter = 1
        print("\nValid Paths for pages:")
        for root, dirs, files in os.walk(f"instances/{app_name}/content"):
            root = root.replace("\\", "/").replace(f"instances/{app_name}/content", "")
            for file in files:
                file_dir = os.path.join(root, file)
                if file_dir[0] == "/" or file_dir[0] == "\\":
                    file_dir = file_dir[1:].replace("\\", "/")
                print(f"{colours['gray' if counter % 2 == 0 else 'white']}File {counter}: {file_dir}")
                counter += 1
        print(colours['white']+"\n")
        input("Press enter to continue and erase this message...")

    def add_page(app_name:str):
        '''Adds a page to the warden.'''
        # Uses os.walk to go through every file in the content directory and subdirs and list their directories
        while True:
            valid_pages = {}
            print("Valid Paths for pages:\n")
            counter = 1
            for root, dirs, files in os.walk(f"instances/{app_name}/content"):
                root = root.replace("\\", "/").replace(f"instances/{app_name}/content", "")
                for file in files:
                    file_dir = os.path.join(root, file)
                    if file_dir[0] == "/" or file_dir[0] == "\\":
                        file_dir = file_dir[1:].replace("\\", "/")
                    print(f"{colours['gray' if counter % 2 == 0 else 'white']}File {counter}: {file_dir}")
                    valid_pages[counter] = file_dir
                    counter += 1
            print("\nType 'exit' to exit.")
            page_dir = input("Relative Page directory: ")
            if page_dir == "exit":
                return

            # Checks if the page is valid
            if page_dir not in valid_pages.values():
                print("Invalid page.\n")
                continue
            # Makes sure the page isn't already added
            if page_dir in jmod.getvalue(key="warden.pages",json_dir=f"instances/{app_name}/config.json",dt=web_config_dt,default=[],):
                print("Page already added.\n")
                continue
            break

        jmod.addvalue(
            key="warden.pages",
            json_dir=f"instances/{app_name}/config.json",
            dt=web_config_dt,
            value=page_dir,
        )
        print("Page added.")

    def rem_page(app_name:str):
        '''Removes a page from the warden.'''
        # Uses os.walk to go through every file in the content directory and subdirs and list their directories
        while True:
            valid_pages = {}
            print("Valid Paths for pages:\n")
            counter = 1
            for root, dirs, files in os.walk(f"instances/{app_name}/content"):
                root = root.replace("\\", "/").replace(f"instances/{app_name}/content", "")
                for file in files:
                    file_dir = os.path.join(root, file)
                    if file_dir[0] == "/" or file_dir[0] == "\\":
                        file_dir = file_dir[1:].replace("\\", "/")
                    print(f"{colours['gray' if counter % 2 == 0 else 'white']}File {counter}: {file_dir}")
                    valid_pages[counter] = file_dir
                    counter += 1
            print("\nType 'exit' to exit.")
            page_dir = input("Relative Page directory: ")
            if page_dir == "exit":
                return

            # Checks if the page is valid
            if page_dir not in valid_pages.values():
                print("Invalid page.\n")
                continue
            # Makes sure the page is already added
            if page_dir not in jmod.getvalue(key="warden.pages",json_dir=f"instances/{app_name}/config.json",dt=web_config_dt,default=[],):
                print("Page not found.\n")
                continue
            break

        jmod.remvalue(
            key="warden.pages",
            json_dir=f"instances/{app_name}/config.json",
            dt=web_config_dt,
            value=page_dir,
        )
        print("Page removed.")

    def change_password(app_name:str):
        '''Changes the password for the warden.'''
        while True:
            password = input("New password: ")
            if password == "":
                print("Password cannot be empty.")
                continue
            break
        jmod.setvalue(
            key="warden.pin",
            json_dir=f"instances/{app_name}/config.json",
            dt=web_config_dt,
            value=password,
        )
        print("Password changed.")