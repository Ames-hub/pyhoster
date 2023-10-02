import os, shutil, logging, docker
from .application import application as app
from .jmod import jmod
from .data_tables import config_dt

class instance: # Do not use apptype in calls until other apptypes are made
    def create(do_autostart: bool = False, apptype: app.types.webpage = app.types.webpage):
        # Gets input if not provided
        input() # This input statement catches the 'create' text entered to call this def. Its purely aesthetic, not functional.
        while True:
            try:
                print("Type Cancel to cancel creation.")
                app_name: str = str(input("What is the name of the app? TEXT : "))
                if app_name.lower() == "cancel":
                    print("Cancelled!")
                    return True
                assert app_name.lower() != "create", "The name cannot be 'create'!" # Prevents the app from being named create as it is a reserved word

                # Makes sure the app name is valid and can be made into a directory folder
                assert not app_name.startswith(" "), "The name cannot start with a space!"
                assert not app_name.endswith(" "), "The name cannot end with a space!"
                assert "." not in app_name, "The name cannot have a period!"
                assert "/" not in app_name and "\\" not in app_name, "The name cannot contain a slash!"
                assert "_" not in app_name, "The name cannot contain an underscore!"
                assert "-" not in app_name, "The name cannot contain a dash!"
                assert ":" not in app_name, "The name cannot contain a colon!"
                assert app_name != "", "The name cannot be blank!"
                
                if app_name in os.listdir("instances/"):
                    raise AssertionError("The name cannot be the same as an existing app!")
                
                break
            except AssertionError as err: # Forces the name to be valid
                print(str(err))
                continue
        
        # Gets the app description
        while True:
            try:
                print("\nInstructions: <nl> = new line")
                app_desc: str = str(input("What is the app's description? TEXT (optional) : "))
                if app_desc.lower() == "cancel":
                    print("Cancelled!")
                    return True
                assert type(app_desc) == str, "The description must be a string!"
                if app_desc == "":
                    app_desc = "A Website hosted by Pyhost."
                app_desc.replace("<nl>", "\n") # Replaces <nl> with a new line
                break
            except AssertionError as err: # Forces the description to be valid
                print(str(err))
                continue

        while True:
            try:
                port: int = input("What port should the app run on? NUMBER (Default: 80) : ")
                if str(port).lower() == "cancel":
                    print("Cancelled!")
                    return True
                if str(port) == "":
                    port = 80
                assert type(int(port)) is int, "The port must be an integer!"
                port = int(port)
                assert port > 0 and port < 65535, "The port must be between 0 and 65535!"
                break
            except (AssertionError, ValueError) as err: # Forces the port to be valid
                print(str(err))
                continue

        while True:
            try:
                boundpath: str = str(input("What is the full path to the app's content? TEXT (blank for no external binding) : "))
                if str(boundpath).lower() == "cancel":
                    print("Cancelled!")
                    return True
                if boundpath != "":
                    assert os.path.exists(boundpath) and os.path.isabs(boundpath), "The path must exist and be absolute! (absolute: starting from root directory such as C:/)"
                else:
                    boundpath = f"instances/{app_name}/"
                break
            except AssertionError as err: # Forces the path to be valid and absolute
                print(str(err))
                continue
        
        while True:
            try:
                do_autostart: str = input("Should the app autostart? Y/N : ").lower()
                if do_autostart == "cancel":
                    print("Cancelled!")
                    return True
                if "y" in do_autostart:
                    do_autostart = True
                elif "n" in do_autostart:
                    do_autostart = False
                else:
                    raise AssertionError("The autostart must be either 'Y' or 'N'!")
                assert type(do_autostart) is bool, "The autostart must be a boolean!"
                break
            except AssertionError as err: # Forces the autostart to be valid
                print(str(err))
                continue

        # Makes the appropriate directories
        os.makedirs(f"instances/{app_name}/", exist_ok=True)
        os.makedirs(f"instances/{app_name}/content/", exist_ok=True)
        # Copies all the content from the absolute path to the app's content folder using shutil
        if boundpath != f"instances/{app_name}/":
            shutil.copytree(boundpath, f"instances/{app_name}/content/", dirs_exist_ok=True)

        from .autostart import autostart
        # Sets the autostart and creates config.json if applicable
        if do_autostart == True:
            autostart.add(app_name)

        # Sets the absolute path/boundpath in the json file
        jmod.setvalue(
            f"{app_name}.boundpath",
            f"instances/{app_name}/config.json",
            value=boundpath,
            dt=config_dt(app_name)
            )
        # Sets description
        jmod.setvalue(
            "description",
            f"instances/{app_name}/config.json",
            value=app_desc,
            dt=config_dt(app_name)
            )


        os.system('cls' if os.name == "nt" else "clear")
        # Prints with green
        print("\033[92m" + f"Created app \"{app_name}\" successfully!" + "\033[0m")
        logging.info(f"Created app \"{app_name}\" successfully!")

    def delete():
        input() # This input statement catches the 'delete' text entered to call this def. Its purely aesthetic, not functional.
        try: # Asks for the app name
            os.system('cls' if os.name == "nt" else "clear")
            print("\nWARNING: "+"\033[91m"+"YOU ARE ABOUT TO DELETE AN APP\n"+"\033[0m"+"All app names below...\n")
            for app in os.listdir("instances/"):
                print(app)
                # Prints description in gray then resets to white
                print("\033[90m"+jmod.getvalue(key="description", json_dir=f"instances/{app}/config.json")+"\033[0m")
            else:
                print("\nType Cancel to cancel deletion.")
            app_name: str = str(input("What is the name of the app? TEXT : "))
            if app_name.lower() == "cancel":
                print("Cancelled!")
                return True
            assert app_name in os.listdir("instances/"), "The app must exist!"
        except AssertionError as err:
            print(str(err))

        try:
            inp = input(f"Are you sure you want to delete \"{app_name}?\" Press enter to confirm. Otherwise, type cancel then enter to cancel.\n>>> ")
            if inp != "":
                raise AssertionError("Cancelled!")
        except AssertionError as err:
            print(str(err))
            return
        
        # Deletes the app's folder
        shutil.rmtree(f"instances/{app_name}/")

        # Prints in green
        print("\033[92m" + f"Deleted app \"{app_name}\" successfully!" + "\033[0m")
        logging.info(f"Deleted app \"{app_name}\" successfully!")

    def manage(app_name, start=True):
        try:
            client = docker.from_env()
            client.ping()  # Check if the Docker daemon is accessible
            
            try:
                # Check if the container exists
                container = client.containers.get(f"{app_name}_nginx")
                
                # If the container exists and we want to start it
                if start:
                    container.start()
                    print(f"Container for {app_name} started.")
                else:
                    # If the container exists but we want to stop it, do nothing and return True
                    print(f"Container for {app_name} already exists.")
                    return True
                
            except docker.errors.NotFound:
                if start:
                    # If the container does not exist and we want to start it, create and start it
                    image_name = "nginx:latest"
                    preferred_port = jmod.getvalue(key=f"{app_name}.port", json_dir=f"instances/{app_name}/config.json")
                    container = client.containers.create(
                        image=image_name,
                        name=f"{app_name}_nginx",
                        ports={f'{preferred_port}/tcp': preferred_port},
                        volumes={f"./instances/{app_name}/content": {'bind': '/usr/share/nginx/html', 'mode': 'ro'}}
                    )
                    container.start()
                    print(f"Container for {app_name} created and started.")
                else:
                    # If the container does not exist and we want to stop it, do nothing and return True
                    print(f"Container for {app_name} does not exist.")
                    return True
                    
        except docker.errors.DockerException as e:
            raise RuntimeError(f"Error accessing Docker: {e}")