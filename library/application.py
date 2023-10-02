import logging, os
import keyboard # Import keyboard for listening for input, not explicitly doing so with input() as it is blocking and can only be used once
class application:
    def run(keybind_listen:bool=True):

        # List of triggers for all word listeners
        # Adds a capital version of each trigger, making all keys a trigger

        trigger_list = ['enter']
        logging.info("All triggers have been added to the trigger list!")

        from .instance import instance
        if keybind_listen == True:
            # Begins listening for create, delete, edit, etc commands
            keyboard.add_word_listener("create", lambda: instance.create(), triggers=trigger_list)
            keyboard.add_word_listener("delete", lambda: instance.delete(), triggers=trigger_list)
            keyboard.add_word_listener("cls", lambda: os.system("cls" if os.name == "nt" else "clear"), triggers=trigger_list)
        else:
            logging.warning("Keybind listening is disabled. To enable it, set keybind_listen to True in application.run() on file pyhost.py or setting an environment variable called PYHOST_KEYBIND_LISTEN to string 'True'.")
            logging.warning("KEYBIND LISTENING BEING DISABLED DISABLES MAJOR PORTIONS OF PYHOST FEATURES.")
            # Prints red
            print("\033[91m" + "Keybind listening is disabled. More information in log file." + "\033[0m")

        try:
            while True:
                pass
        except KeyboardInterrupt:
            os.system('cls' if os.name == "nt" else "clear")
            print("Exit signal recieved: Program is now exiting.")
            logging.info("Exit signal recieved: Program is now exiting.")
            logging.shutdown()
            exit(1)

    class types:
        def webpage():
            return "WEBPAGE"