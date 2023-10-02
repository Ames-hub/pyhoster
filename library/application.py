import logging, keyboard
class application:
    def run(keybind_listen:bool=True):

        raw_trigger_list = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'] # List of triggers for all word listeners
        # Adds a capital version of each trigger, making all keys a trigger
        trigger_list = []
        for trigger in raw_trigger_list:
            trigger_list.append(trigger.upper())
            trigger_list.append(trigger.lower())

        trigger_list.append("enter")
        trigger_list.append("space")
        del raw_trigger_list
        logging.info("All triggers have been added to the trigger list!")

        from .instance import instance
        if keybind_listen == True:
            # Begins listening for create, destroy, edit, etc commands
            keyboard.add_word_listener("create", lambda: instance.create(), triggers=trigger_list, match_suffix=True)
        else:
            logging.warning("Keybind listening is disabled. To enable it, set keybind_listen to True in application.run() on file pyhost.py or setting an environment variable called PYHOST_KEYBIND_LISTEN to string 'True'.")
            logging.warning("KEYBIND LISTENING BEING DISABLED DISABLES MAJOR PORTIONS OF PYHOST FEATURES.")
            # Prints red
            print("\033[91m" + "Keybind listening is disabled. More information in log file." + "\033[0m")

        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("Exit signal recieved: Program is now exiting.")
            logging.info("Exit signal recieved: Program is now exiting.")
            logging.shutdown()
            exit(1)

    class types:
        def webpage(self):
            return self.webpage # Does not make a loopback, just returns the function
            