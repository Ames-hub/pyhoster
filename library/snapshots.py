import os, shutil, hashlib, time, sys
try:
    from .jmod import jmod
    from .pylog import pylog
    from .data_tables import app_settings, web_config_dt
except ImportError as err:
    print("Hello! To run Pyhost, you must run the file pyhost.py located in this projects root directory, not this file.\nThank you!")
    from library.pylog import pylog
    pylog().error(f"Import error in {__name__}", err)
    exit()

setting_dir = "settings.json"
pylogger = pylog()
four_hours = 14400 # 4 hours in seconds

orange = "\033[93m"
cyan = "\033[96m"
green = "\033[92m"
white = "\033[0m"
gray = "\033[90m"

class snapshots:
    """
    A class containing functions for creating and managing snapshots of app instances.
    """
    def update(app_name=None, is_interface=False):
        """
        Updates the specified app by copying files from the external directory (boundpath) to the internal directory (content_dir).
        If is_interface is True or app_name is None, it prompts the user to select an app to update.
        If the content directory is not empty, it takes a snapshot of the current content directory before updating.
        It then removes all old files and directories from the content directory.
        Finally, it duplicates all files from the boundpath to the content directory.

        Args:
            app_name (str, optional): The name of the app to update. If None, the user will be prompted to select an app. Defaults to None.
            is_interface (bool, optional): Indicates whether the update is being performed through an interface. Defaults to False.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        if is_interface == True or app_name == None:
            app_name = snapshots.get_rollback_app(variant=3)
            if type(app_name) is not str:
                return False
        
        # Overwrites internal with external directory
        boundpath = jmod.getvalue(key="boundpath", json_dir=f"instances/{app_name}/config.json")
        content_dir = jmod.getvalue(key="contentloc", json_dir=f"instances/{app_name}/config.json")
        # Takes a snapshot of the current content directory to back it up
        if os.listdir(content_dir) != []:
            if jmod.getvalue(key="do_autobackup", json_dir=setting_dir, dt=app_settings) == True:
                snapshots.backup(app_name=app_name, is_interface=False)
                print("Phase 1 completed: Snapshot taken.")
            else:
                print("Phase 1 Skipped: Auto Snapshots are disabled.")
        else:
            print("Phase 1 Skipped: Content directory is empty.")
        # Removes all old files and directories

        cleared_content = snapshots.clear_content(content_dir)
        clear_msg = f"{cleared_content[2]}/{cleared_content[1]}"
        print(f"Update phase 2 completed: Old File removal. {clear_msg}")

        # Updates all files
        shutil.copytree(src=boundpath, dst=content_dir, dirs_exist_ok=True)
        print("Phase 3 completed: File duplication\n"+"\033[92m"+"Update completed."+"\033[0m")
        jmod.setvalue(
            key="last_updated",
            json_dir=f"instances/{app_name}/config.json",
            value=time.time(),
            dt=web_config_dt
        )

    def clear_content(content_dir):
        '''
        def for clearing content so it can be updated.

        returns tuple of (bool, int, int)
        bool[0]: True if the operation was successful, False otherwise.
        int[1]: The number of files ran through.
        int[2]: The number of files completed.
        '''
        files_ranthrough = 0
        files_complete = 0
        for item in os.listdir(content_dir):
            item_path = os.path.join(content_dir, item)
            files_ranthrough += 1
            try:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    files_complete += 1
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    files_complete += 1
            except PermissionError as err:
                print("Permission error: Unable to remove a file or directory.")
                pylogger.error("Permissions error: Unable to remove a file or directory.", err)
            except Exception as err:
                print("An error occurred while removing a file or directory:")
                print(str(err))
                # Logs the error
                pylogger.error("Can't remove a file or directory.", err)

        return (True, files_ranthrough, files_complete,)

    def check_outdated(app_name: str, boundpath_only: bool = False):
        '''
        Returns a boolean indicating whether an app is outdated.

        Args:
            app_name (str): The name of the app.
            boundpath_only (bool, optional): Indicates whether to only check the boundpath.
            Defaults to False.
        Returns:
            bool: True if the app is outdated, False otherwise.
            -1: if the user has not set an external bound path and its needed/wanted. (happens only with boundpath_only=True)
            -2: if there is not a external boundpath and there are no previous backups to compare it to.
        '''
        def calculate_file_hash(file_path):
            BLOCKSIZE = 65536
            hasher = hashlib.sha1()
            file_path = str(file_path)
            if os.path.isdir(file_path) or file_path.endswith('.log'):
                return None
            with open(file_path, 'rb') as file:
                buf = file.read(BLOCKSIZE)
                while len(buf) > 0:
                    hasher.update(buf)
                    buf = file.read(BLOCKSIZE)
            file_hash = hasher.hexdigest()
            return file_hash

        def get_file_hashes(directory):
            file_hashes = {}
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, directory)
                    file_hash = calculate_file_hash(file_path)
                    if file_hash is not None:
                        file_hashes[relative_path] = file_hash
            return file_hashes

        boundpath = jmod.getvalue(key="boundpath", json_dir=f"instances/{app_name}/config.json")
        app_dir = jmod.getvalue(key="contentloc", json_dir=f"instances/{app_name}/config.json")

        # app_dir and boundpath start in the content_dir, so move 1 directory up.
        app_dir = os.path.abspath(os.path.join(app_dir, ".."))  # .. is up one directory
        boundpath = os.path.abspath(os.path.join(boundpath, ".."))

        # Changes the boundpath for if the app's boundpath == content_dir
        if boundpath_only == False:
            if boundpath == app_dir:
                boundpath = snapshots.get_backup_dir(app_name)  # returns something like .../pyhoster/backups/<appname>/(versions list, formatted as "ver<ver number>")

                # Gets the latest version
                highest_ver = len(os.listdir(boundpath))
                if highest_ver == 0:
                    return -2 # No backups to compare to
                boundpath = os.path.join(boundpath, f"ver{highest_ver}/")  # Sets the boundpath to the highest version
        else:
            return -1

        # Get the file hashes for each file in the external (boundpath) directory
        ext_hashes = get_file_hashes(boundpath)

        # Get the file hashes for each file in the internal (content_dir) directory
        int_hashes = get_file_hashes(app_dir)

        # Check for outdated files
        outdated = ext_hashes != int_hashes

        return outdated

    def get_backup_dir(app_name):
            """
            Gets the directory to backup the app instance to.

            Parameters:
            app_name (str): The name of the app instance.

            Returns:
            str: The absolute path of the backup directory.
            """
            backup_dir = jmod.getvalue(key="backups_path", json_dir=setting_dir, dt=app_settings)
            if backup_dir != None: 
                backup_dir = os.path.join(backup_dir, app_name)
            if backup_dir == None: # None means nothing was set by the user as a preference
                linux = sys.platform == "linux"
                if linux:
                    # No idea how to store backups outside of CWD without permission errors on Linux.
                    # Only solution is to store it in the CWD until we get backups-over-ftp working.
                    backup_dir = f"pyhoster/backups/{app_name}/"
                else:
                    # Gets the appdata directory for the user
                    appdata = os.getenv("APPDATA")
                    backup_dir = f"{appdata}/pyhoster/backups/{app_name}/"
            backup_dir = os.path.abspath(backup_dir)
            os.makedirs(backup_dir, exist_ok=True)
            return backup_dir

    def get_rollback_app(variant:int) -> str:
        """
        Retrieves the name of an app from the user.

        Returns:
            bool: False if the operation is cancelled, Returns name (str) otherwise.
        """
        assert type(variant) is int, "variant must be an integer!"
        if variant == 1:
            timenow = time.time()
            while True:
                try:
                    print("\nAll app names below. Descriptions are in "+gray+"gray"+white)
                    print("Apps which were recently updated (4h ago maximum) are highlighed "+orange+"orange!"+white)
                    print(f"If the app was not updated recently, it will be highlighted {green}green{white}.")
                    print(f"And if we can't tell how long ago it was, we'll use {cyan}cyan{white}.\n")
                    for app in os.listdir("instances/"):
                        last_updated = jmod.getvalue(key="last_updated", json_dir=f"instances/{app}/config.json")
                        app_desc = str(jmod.getvalue(key="description", json_dir=f"instances/{app}/config.json")).replace("<nl>","\n")
                        if last_updated == None:
                            print(cyan+app+white)
                            print(gray+app_desc+white) # Time is unknown, print with cyan

                        elif last_updated != None:
                            # If its been less than 4 hours, print with orange
                            if timenow - last_updated <= four_hours:
                                print(orange+app+white)
                                print(gray+app_desc+white)
                            else: # its been more than 4 hours, print with white
                                print(app)
                                print(gray+app_desc+white)

                    app_name = input("What is the name of the app you wish to rollback? TEXT : ")
                    if app_name.lower() == "cancel":
                        print("Cancelled!")
                        return False
                    assert app_name in os.listdir("instances/"), "The app must exist to be rolled back!"
                    break
                except AssertionError as err:
                    print(str(err))
                    continue
        elif variant == 2:
            while True:
                try:
                    print("\n")
                    for app in os.listdir("instances/"):
                        print(app)
                        print("\033[90m"+str(jmod.getvalue(key="description", json_dir=f"instances/{app}/config.json")).replace("<nl>","\n")+"\033[0m")
                    else:
                        print("\nType Cancel to cancel the backup.")

                    app_name = input("What is the name of the app you wish to backup? TEXT : ").lower()
                    if app_name == "cancel":
                        print("Cancelled!")
                        return True
                    
                    assert app_name in os.listdir("instances/"), "The app must exist!"
                    break # Breaks the loop if it passes the assertion tests
                except AssertionError as err:
                    print(str(err))
                    continue
        elif variant == 3:
            while True:
                try:
                    print("\nAll app names below...\nDescriptions are in " + "\033[90m" + "gray" + "\033[0m \nName is "+"\033[91m"+"red"+"\033[0m"+" if outdated, "+"\033[96m"+"cyan"+"\033[0m"+" if up to date and finally "+"\033[93m"+"yellow"+"\033[0m"+" if the content folder is empty\n")
                    for app in os.listdir("instances/"):
                        # Get the paths for external (boundpath) and internal (content_dir) directories
                        content_dir = jmod.getvalue(key="contentloc", json_dir=f"instances/{app}/config.json")

                        if os.listdir(content_dir) == []: # Prints in yellow to indicate empty
                            print("\033[93m" + app + "\033[0m")
                            continue # Continue, nothing to compare.

                        outdated = snapshots.check_outdated(app_name=app, boundpath_only=True)

                        description = "\033[90m" + str(jmod.getvalue(key="description", json_dir=f"instances/{app}/config.json")).replace("<nl>","\n") + "\033[0m"
                        if outdated == False:
                            print("\033[96m" + app + "\033[0m\n"+description) # prints cyan
                        elif outdated == True:
                            print("\033[91m" + app + "\033[0m\n"+description) # Prints red
                        elif outdated in [-1, -2]: # no boundpath result, stops it from looking in an old backup folder.
                            pass # don't print it, so the user doesn't see it as an option to do so
                        else:
                            print(app+"\n"+description)

                    app_name = input("\nPlease enter the app name to update. Press enter to refresh.\n>>> ")
                    if app_name == "cancel":
                        print("Cancelled!")
                        return True
                    elif app_name in os.listdir("instances/"):
                        break
                except PermissionError as err:
                    print("We encountered a permissions error while trying to read if an app is outdated!")
                    pylogger.error("Permissions error encountered!", err)
                    return False

        return app_name

    def rollback(app_name=None, is_interface=False, rollback_ver=None):
        """
        Rollbacks the specified app to a previous version.

        Args:
            app_name (str, optional): The name of the app to rollback. Defaults to None.
            is_interface (bool, optional): Indicates whether the app is an interface. Defaults to False.
            rollback_ver (str, optional): The version to rollback to. Defaults to None.

        Returns:
            bool: True if the rollback was successful, False otherwise.
        """
        timenow = time.time()
        if is_interface == True or app_name == None:
            app_name = snapshots.get_rollback_app(variant=1)
            if type(app_name) is not str:
                return False

        backup_dir = snapshots.get_backup_dir(app_name)

        # Creates the backup directory if it doesn't exist
        os.makedirs(backup_dir, exist_ok=True)
        # Lists out all the versions and their last modified time
        
        # Gets if it IS running so it wont be started up if it wasn't running before
        was_running = jmod.getvalue(key="running", json_dir=f"instances/{app_name}/config.json")
        from .instance import instance
        instance.stop(app_name=app_name) # stops the app, as its about to be overwritten
        
        if is_interface == True or rollback_ver == None:
            print(
            "\nAll snapshots of the app can be seen below. If it was recently added, its "+orange+"orange"+white+", else its "+green+"green"+white+"."
            )
            for version in os.listdir(backup_dir):
                try:
                    last_modified = os.path.getmtime(os.path.join(backup_dir, version))
                    if timenow - last_modified <= four_hours:
                        print(orange+version+white)
                    else:
                        print(green+version+white)
                except:
                    print(version+" | WARNING: POTENTIALLY UNSTABLE! (Last modified time could not be found.)")

            while True:
                try:
                    rollback_ver = input("What version do you wish to rollback to? TEXT : ")
                    if rollback_ver == "cancel":
                        print("Cancelled!")
                        return True
                    assert rollback_ver in os.listdir(backup_dir), "The version must exist to be rolled back to!"
                    break
                except AssertionError as err:
                    print(str(err))
                    continue
        
        # Validates rollback_ver as a version
        try:
            assert rollback_ver in os.listdir(backup_dir), "The version must exist to be rolled back to!"
        except AssertionError as err:
            print(str(err))
            return
        
        # Completely overwrites current app with backup
        shutil.rmtree(f"instances/{app_name}/")
        print("Phase 1 completed.")
        shutil.copytree(src=os.path.join(backup_dir, rollback_ver), dst=f"instances/{app_name}/", dirs_exist_ok=True)
        print("Phase 2 completed.")

        # Starts the app again
        if was_running:
            instance.start_interface(app_name, is_interface=False),
        else:
            print("App was not running before. Autostart cancelled.")

        pylogger.info(f"Rollback of \"{app_name}\" completed! (Version {rollback_ver})")

        print(green+"Rollback completed!"+white)

    def backup(app_name=None, is_interface=True, do_alert=False):
        """
        Creates a backup of the specified app instance.

        Args:
            app_name (str, optional): The name of the app instance to backup. Defaults to None.
            is_interface (bool, optional): Indicates whether the backup is triggered from the interface. Defaults to True.
            do_alert (bool, optional): Indicates whether to display an alert message. Defaults to False.
        """
        if app_name == None or is_interface == True:
            app_name = snapshots.get_rollback_app(variant=2)
            if type(app_name) is not str:
                return False
   
        # Gets the directory to backup the app instance to
        backup_dir = snapshots.get_backup_dir(app_name)

        # Creates the backup directory if it doesn't exist
        os.makedirs(backup_dir, exist_ok=True)

        # Gets the version of the snapshot by listing the directory
        version = "ver"+str(len(os.listdir(backup_dir)) + 1)
        backup_dir = os.path.join(backup_dir, version) # Adds the version to the backup directory

        # Gets the directory of the app
        app_dir = os.path.abspath(f"instances/{app_name}/")
        try:
            # copies the app directory to the backup directory
            shutil.copytree(src=app_dir, dst=backup_dir, dirs_exist_ok=True)

            if do_alert == True or is_interface == True: 
                print(f"Snapshot of \"{app_name}\" completed! (Version {version})")
                pylogger.info(f"Snapshot of \"{app_name}\" completed! (Version {version})")
        except Exception as err:
            if do_alert:
                print(f"Failed to create snapshot of \"{app_name}\": {err}")
            pylogger.error(f"Failed to create snapshot of \"{app_name}\"", err)
