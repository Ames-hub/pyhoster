# Import the necessary modules
import logging
import os
import keyboard
import threading
import ctypes  # Import ctypes to forcefully terminate a thread

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
                        thread.join(timeout=2)  # Wait for the thread to finish for a maximum of 2 seconds
                    except Exception as e:
                        logging.error(f"Error stopping thread: {e}")
                        # Forcefully terminate the thread if an exception occurs
                        thread_id = ctypes.c_long(thread.ident)
                        ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
                        logging.info(f"terminated thread: {thread}")
            print("All web instances have been shut down.")

            # Sets all the JSON file's running key to False
            from .jmod import jmod
            from .data_tables import config_dt

            print("Setting all instances to not running...")
            for app in os.listdir("instances/"):
                jmod.setvalue(
                    key="running",
                    json_dir=f"instances/{app}/config.json",
                    value=False,
                    dt=config_dt(app)
                )
            print("All instances have been set to not running.")

            print("Exiting...")
            exit(1)

    class types:
        def webpage():
            return "WEBPAGE"