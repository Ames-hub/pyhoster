from ..jmod import jmod
from ..data_tables import app_settings
from ..userman import userman
import waitress, os, multiprocessing, time

from ..pylog import pylog
apipylog = pylog(filename="logs/api/%TIMENOW%.log")

colours = {
    "red": "\033[91m",
    "green": "\033[92m",
    "blue": "\033[94m",
    "yellow": "\033[93m",
    "white": "\033[0m",
    "purple": "\033[95m",
    "cyan": "\033[96m"
}

class controller:
    def StartFlask():
        '''
        Create a WSGI Server set primarily for Flask.
        '''
        app_dir = jmod.getvalue("api.app_dir", "settings.json", "library.API.MainAPI", app_settings)
        port = jmod.getvalue("api.port", "settings.json", 4045, app_settings)
        app = __import__(app_dir, fromlist=['']).app
        os.environ["FLASK_ENV"] = "production"  # Set Flask environment to production
        os.environ["FLASK_APP"] = "PyHostAPI"  # Set the name of your Flask app
        apipylog.info(f"Starting PyHost API on port {port}")
        print(f"<--PyHost API is Online running on port {port} and awaiting requests-->")
        try:
            waitress.serve(app, host='0.0.0.0', port=port)
        except PermissionError:
            print(f"We don't have enough permissions to run the API! Is there already an app bound to port \"{port}\"?")
            if port < 1024 and os.name != "nt":
                print("If you are running on Linux, then the port must be greater than 1024.")
            return
        time.sleep(0.5) # Prevent the above print from being put on the "enter command" input line

    def timeout_login(interval_min=1):
        '''
        Logs out the user after a certain amount of time.
        '''
        while True:
            try:
                time.sleep(interval_min * 60)
            except:
                return
            user_list = userman.list_users(for_CLI=False)
            for user in user_list:
                if user_list[user]["api"]["logged_in"] is True:
                    userman.user(user).logout_api()
                    apipylog.info(f"User {user} has been logged out due to inactivity.")

    def initapi():
        API_Process = multiprocessing.Process(
            target=controller.StartFlask, args=()
            )
        API_Process.start()
        jmod.setvalue(
            key="api.pid",
            json_dir="settings.json",
            value=API_Process.pid,
            dt=app_settings
        )
        jmod.setvalue(
            key="api.running",
            json_dir="settings.json",
            value=True,
            dt=app_settings
        )

        # Starts the login timeout routine
        timeout_process = multiprocessing.Process(
            target=controller.timeout_login, args=()
            )
        timeout_process.start()
        jmod.setvalue(
            key="api.timeout_pid",
            json_dir="settings.json",
            value=timeout_process.pid,
            dt=app_settings
        )

        time.sleep(0.5) # Wait for the API and its processes to start

    def stopapi():
        '''
        Stops the API.
        '''
        pid = jmod.getvalue("api.pid", "settings.json", None, app_settings)
        try:
            os.kill(pid, 2)
        except:
            try:
                os.kill(pid, 9)
            except:
                return False
        
        jmod.setvalue(
            key="api.running",
            json_dir="settings.json",
            value=False,
            dt=app_settings
        )
        jmod.setvalue(
            key="api.pid",
            json_dir="settings.json",
            value=None,
            dt=app_settings
        )
        apipylog.info("PyHost API has been stopped.")
        return True

    def is_running():
        '''
        Checks if the API is running.
        '''
        return jmod.getvalue("api.running", "settings.json", False, app_settings)

    def status(interface:bool):
        apirunning = controller.is_running()
        
        if interface:
            if apirunning is False:
                print("The API is not running.")
                return
            else:
                print("The API is running.")

        port = jmod.getvalue("api.port", "settings.json", 4045, app_settings)
        if interface: print(f"The API Is bound to Port {port}")
        
        return {"running": apirunning, "port": port}

    def enter():
        '''
        CLI to interact with the API.
        '''
        os.system("cls" if os.name == "nt" else "clear")
        while True:
            print("<--PYHOST API COMMAND LINE INTERFACE-->")
            print("Type 'exit' to exit the CLI. Type 'help' for help")
            status = controller.status(interface=False) # print the status of the API
            print(f"The API Is Running and Bound to port {status['port']}" if status['running'] else f"\
The API is not running but is set for port {status['port']}.")

            command = input(f"{colours['red' if status['running'] is False else 'green']}api{colours['white']}> ")
            if command == "stop":
                controller.stopapi()
                continue
            elif command == "start":
                print("Starting the API...")
                multiprocessing.Process(target=controller.initapi, args=()).start()
                time.sleep(1)
                continue
            elif command == "exit":
                return
            elif command == "help":
                controller.help_msg()
                continue
            elif command == "port":
                controller.change_port()
                continue
            elif command == "autoboot":
                controller.autoboot()
                continue
            elif command == "actions":
                controller.actionprint()
                continue
            elif command == "viewlogs":
                controller.viewlogs()
                continue
            elif command == "cls":
                os.system("cls" if os.name == "nt" else "clear")
                continue
            else:
                print("Invalid Command.\n")
                continue

    def help_msg():
        '''
        Prints the help message for the API CLI.
        '''
        print("stop - Stops the API.")
        print("start - Starts the API.")
        print("port - Changes the port the API is bound to.")
        print("autoboot - Sets the API to start on boot.")
        print("actions - Choose if the API should log or print actions.")
        print("viewlogs - View the API logs.")
        print("cls - Clears the screen.")
        print("exit - Exits the CLI.")
        input("Press Enter to continue.\n")

    def viewlogs():
        print(f"{colours['yellow']}You are currently viewing logs for the API.\nPress CTRL+C or Enter to exit.{colours['white']}\n")
        controller.actionprint(mode=True, is_interface=False) # Allows the API actions to be printed
        try:
            input("")
        except KeyboardInterrupt:
            pass
        finally:
            print(colours["white"])
            controller.actionprint(mode=False, is_interface=False)
            return True

    def actionprint(mode=True, is_interface=True) -> bool:
        '''
        Choose if the API should log actions.
        '''
        if is_interface:
            while True:
                print("Would you like to print API actions?")
                mode = input("Y/N: ").lower()
                if mode == "y":
                    print(f"{colours['green']}The API will now print actions.{colours['white']}")
                    mode = True
                    break
                elif mode == "n":
                    print(f"{colours['red']}The API will not print actions.{colours['white']}")
                    mode = False
                    break
                else:
                    print("Invalid Input.\n")
                    continue

        jmod.setvalue(
            key="api.actionprint",
            json_dir="settings.json",
            value=mode,
            dt=app_settings
        )
        return True

    def autoboot(is_interface=True, autoboot=True):
        '''
        Sets the API to start on boot.
        '''
        if is_interface:
            while True:
                print("Would you like to set the API to start on boot?")
                autoboot = input("Y/N: ").lower()
                if autoboot == "y":
                    print(f"{colours['green']}The API will now start on boot.{colours['white']}")
                    autoboot = True
                    break
                elif autoboot == "n":
                    print(f"{colours['red']}The API will not start on boot.{colours['white']}")
                    autoboot = False
                    break
                else:
                    print("Invalid Input.\n")
                    continue

        jmod.setvalue(
            key="api.autoboot",
            json_dir="settings.json",
            value=autoboot,
            dt=app_settings
        )

    def change_port(port=4040, is_interface=True, print_success=True):
        '''
        Changes the port the API is bound to.
        '''
        if is_interface:
            while True:
                port = input("Enter the new port for the API: ")
                if port.isdigit() is False:
                    print("Please enter a valid port number.")
                    continue
                break
        jmod.setvalue(
            key="api.port",
            json_dir="settings.json",
            value=int(port),
            dt=app_settings
        )
        if print_success: print(f"The API is now set to port {port}.")
        if is_interface:
            while True:
                print("Would you like to restart the API to apply the change?")
                restart = input("Y/N: ").lower()
                if restart == "y":
                    controller.stopapi()
                    controller.initapi()
                    break
                elif restart == "n":
                    break
                else:
                    print("Invalid Input.")
                    continue

        return True