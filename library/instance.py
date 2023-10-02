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
            
            port: int = int(input("What port should the app run on? NUMBER : "))
            
            try:
                boundpath: str = str(input("What is the full path to the app's content? TEXT : "))
                assert os.path.exists(boundpath) and os.path.isabs(boundpath), "The path must exist and be absolute!"
            except AssertionError as err: # Forces the path to be valid and absolute
                print(str(err))
                continue
            assert boundpath is os.path.abspath(boundpath), "The path must be absolute!"

            do_autostart: bool = bool(input("Should the app autostart? Y/N : "))
            break

        # Makes the appropriate directories
        os.makedirs(f"instances/{app_name}", exist_ok=True)