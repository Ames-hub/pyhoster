from ..jmod import jmod
from ..data_tables import app_settings
from ..userman import userman
import waitress, os, multiprocessing, time, logging

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
        port = jmod.getvalue("api.port", "settings.json", 987, app_settings)
        app = __import__(app_dir, fromlist=['']).app
        os.environ["FLASK_ENV"] = "production"  # Set Flask environment to production
        os.environ["FLASK_APP"] = "PyHostAPI"  # Set the name of your Flask app
        logging.info(f"Starting PyHost API on port {port}")
        print(f"<--PyHost API is Online running on port {port} and awaiting requests-->")
        waitress.serve(app, host='0.0.0.0', port=port)

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
                    userman.api.logout(user)
                    logging.info(f"User {user} has been logged out due to inactivity.")

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
        logging.info("PyHost API has been stopped.")
        return True

    def is_running():
        '''
        Checks if the API is running.
        '''
        return jmod.getvalue("api.running", "settings.json", False, app_settings)

    def status(interface:bool):
        apirunning = controller.is_running()
        
        if not interface:
            if apirunning is False:
                print("The API is not running.")
                return
            else:
                print("The API is running.")

        port = jmod.getvalue("api.port", "settings.json", 987, app_settings)
        if interface: print(f"The API Is bound to Port {port}")
        
        return {"running": apirunning, "port": port}

    def enter():
        '''
        CLI to interact with the API.
        '''

        status = controller.status(interface=True) # print the status of the API

        while True:
            command = input(f"{colours['red' if status['running'] is True else 'green']}api{colours['white']}> ")
            if command == "stop":
                controller.stopapi()
                continue
            elif command == "start":
                multiprocessing.Process(target=controller.initapi, args=()).start()
                continue
            elif command == "exit":
                return
            elif command == "cls":
                os.system("cls" if os.name == "nt" else "clear")
                continue
            else:
                print("Invalid Command.")
                continue
