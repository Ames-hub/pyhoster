import logging, os, multiprocessing as mp, json

root_dir = os.getcwd()

class application:
    def run(keybind_listen: bool = True):
        application.running = True

        def help_msg():
            print("Available Commands:")
            if bool(os.environ.get("PYHOST_KEYBIND_LISTEN",True)) == False:
                print("NONE: Input has been disabled. How did you even get here?")
            else:
                print("create: Creates a new app")
                print("delete: Deletes an app")
                print("edit: Edits an app")
                print("start: Starts an app")
                print("restart: Turns off then on an app")
                print("stop: Stops an app")
                print("help: Displays this message")
                print("cls: Clears the screen")

        from .instance import instance
        try:
            while True:
                if keybind_listen == True:
                    cmd: str = str(input("Enter a command: "))
                    # Begins listening for create, delete, edit, etc commands
                    if cmd == "create":
                        instance.create()
                    elif cmd == "delete":
                        instance.delete()
                    elif cmd == "edit":
                        instance.edit()
                    elif cmd == "start":
                        instance.start_interface()
                    elif cmd == "restart":
                        instance.restart_interface()
                    elif cmd == "stop":
                        instance.stop_interface()
                    elif cmd == "help":
                        help_msg()
                    elif cmd == "cls":
                        os.system("cls" if os.name == "nt" else "clear")
                    elif cmd == "":
                        pass # Idk why, but it takes 1 press of enter to have the message appear. weird
                    else:
                        print("Invalid command. Please try again or do `help`")
        except KeyboardInterrupt:
            application.running = False
            # os.system('cls' if os.name == "nt" else "clear")
            print("Exit signal received: Program is now exiting.")
            logging.info("Exit signal received: Program is now exiting.")
            logging.shutdown()

            print("Shutting down all web instances...")
            # Shuts down all the threads that run the webservers
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
                    dt=config_dt
                )
            print("All instances have been set to not running.")

            # Sets all PID's to None
            print("Setting all PID's to None...")
            for app in os.listdir("instances/"):
                jmod.setvalue(
                    key="pid",
                    json_dir=f"instances/{app}/config.json",
                    value=None,
                    dt=config_dt
                )
            print("All PID's have been set to None.")

            print("Exiting...")
            exit(1)

    class types:
        def webpage():
            return "WEBPAGE"