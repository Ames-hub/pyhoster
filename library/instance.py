import os
from .application import application as app
class instance: # Do not use apptype in calls until other apptypes are made
    def create(do_autostart: bool = False, apptype: app.types.webpage = app.types.webpage):
        # Gets input if not provided
        tried = False
        while True:
            try:
                app_name: str = str(input("What is the name of the app? TEXT : "))
                assert app_name.isalnum(), "The name must be alphanumeric!"
                assert app_name.lower() != "create", "The name cannot be 'create'!" # Prevents the app from being named create as it is a reserved word
            except AssertionError as err: # Forces the name to be valid
                if tried == False:
                    print(str(err))
                if "cannot be" in str(err):
                    tried = True
                continue
            
            try:
                port: int = input("What port should the app run on? NUMBER (Default: 80) : ")
                if str(port) == "":
                    port = 80
                assert type(port) is int, "The port must be an integer!"
                port = int(port)
                assert port > 0 and port < 65535, "The port must be between 0 and 65535!"
            except AssertionError as err: # Forces the port to be valid
                print(str(err))
                continue

            try:
                boundpath: str = str(input("What is the full path to the app's content? TEXT : "))
                assert os.path.exists(boundpath) and os.path.isabs(boundpath), "The path must exist and be absolute! (absolute: starting from root directory such as C:/)"
            except AssertionError as err: # Forces the path to be valid and absolute
                print(str(err))
                continue

            try:
                do_autostart: str = input("Should the app autostart? Y/N : ").lower()
                if "y" in do_autostart:
                    do_autostart = True
                elif "n" in do_autostart:
                    do_autostart = False
                else:
                    raise AssertionError("The autostart must be either 'Y' or 'N'!")
                assert type(do_autostart) is bool, "The autostart must be a boolean!"
            except AssertionError as err: # Forces the autostart to be valid
                print(str(err))
                continue
            break

        # Makes the appropriate directories
        os.makedirs(f"instances/{app_name}", exist_ok=True)