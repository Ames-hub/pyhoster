# Import the necessary modules
import logging
import os
import keyboard
import threading
import json

root_dir = os.getcwd()

class application:
    def run(keybind_listen: bool = True):
        # List of triggers for all word listeners
        # Adds a capital version of each trigger, making all keys a trigger

        trigger_list = ['enter']
        logging.info("All triggers have been added to the trigger list!")

        from .instance import instance
        if keybind_listen == True:

            # Begins listening for create, delete, edit, etc commands
            keyboard.add_word_listener("create", lambda: instance.create(), triggers=trigger_list)
            keyboard.add_word_listener("delete", lambda: instance.delete(), triggers=trigger_list)
            keyboard.add_word_listener("start", lambda: instance.start_interface(), triggers=trigger_list)
            keyboard.add_word_listener("stop", lambda: instance.stop_interface(), triggers=trigger_list)
            keyboard.add_word_listener("cls", lambda: os.system("cls" if os.name == "nt" else "clear"), triggers=trigger_list)
        else:
            logging.warning("Keybind listening is disabled. To enable it, set keybind_listen to True in application.run() on file pyhost.py or setting an environment variable called PYHOST_KEYBIND_LISTEN to string 'True'.")
            logging.warning("KEYBIND LISTENING BEING DISABLED DISABLES MAJOR PORTIONS OF PYHOST FEATURES.")
            # Prints red
            print("\033[91m" + "Keybind listening is disabled. More information in the log file." + "\033[0m")

        try:
            while True:
                pass
        except KeyboardInterrupt:
            os.system('cls' if os.name == "nt" else "clear")
            print("Exit signal received: Program is now exiting.")
            logging.info("Exit signal received: Program is now exiting.")
            logging.shutdown()

            print("Shutting down all web instances...")
            # Shuts down all the threads that run the webservers
            for thread in threading.enumerate():
                # Check if the thread is not the main thread
                if thread != threading.current_thread():
                    try:
                        for app in os.listdir("instances/"):
                            config_path = os.path.abspath(f"instances/{app}/config.json")
                            with open(config_path, 'r') as config_file:
                                config_data = json.load(config_file)
                            pid = config_data.get("pid")

                            if pid is None:
                                print(f"PID is not defined in config.json for {app}!")
                                choice = input("Would you like to forcefully terminate? (y/n): ")
                                if choice.lower() == "y":
                                    os.kill(pid, 9)
                                    # signal 9 == SIGKILL
                                else:
                                    print("Skipping...")
                                    continue

                            # Terminate the web server process gracefully.
                            os.kill(pid, 2)
                            # signal 2 == CTRL + C
                    except Exception as e:
                        logging.error(f"Error stopping thread: {e}")
            print("All web instances have been shut down.")

            # Sets all the JSON file's running key to False
            from .jmod import jmod
            from .data_tables import config_dt

            print("Setting all instances to not running...")
            os.makedirs("instances", exist_ok=True)
            for app in os.listdir("instances/"):
                jmod.setvalue(
                    key="running",
                    json_dir=f"instances/{app}/config.json",
                    value=False,
                    dt=config_dt(app)
                )
            print("All instances have been set to not running.")

            # Sets all PID's to None
            print("Setting all PID's to None...")
            for app in os.listdir("instances/"):
                jmod.setvalue(
                    key="pid",
                    json_dir=f"instances/{app}/config.json",
                    value=None,
                    dt=config_dt(app)
                )
            print("All PID's have been set to None.")

            print("Exiting...")
            exit(1)

    class types:
        def webpage():
            return "WEBPAGE"