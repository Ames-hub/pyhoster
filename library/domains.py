try:
    from .jmod import jmod
    from .data_tables import app_settings
    from .pylog import pylog
except ImportError as err:
    print("Hello! To run Pyhost, you must run the file pyhost.py located in this projects root directory, not this file.\nThank you!")
    from library.pylog import pylog
    pylog().error(f"Import error in {__name__}", err)
pylogger = pylog()
class pyhost_domain:
    def get_via_input():
            """
            Prompts the user to enter a domain name and validates it.

            Returns:
            - str: The validated domain name entered by the user.
            """
            while True:
                print("Do you have a domain name you'd like us to use? (eg, example.com or 192.168.0.192)")
                print("If so, enter it here. If not, leave it blank and we'll use the default. (localhost)")
                hostname = input(">>> ").lower()
                if hostname == "":
                    return "localhost"
                if pyhost_domain.parse(hostname):
                    return hostname
                else:
                    print(f'Hostname "{hostname}" does not match the usual format of a domain or IP.')
                    print("Should we use it anyway? (y/n)")
                    use_anyway = input(">>> ").lower()
                    if use_anyway != "n":
                        print("Ignoring invalid format...")
                        return hostname
                    else:
                        print("Retrying...")
                        continue

    def load():
        """
        Loads the hostname from the 'settings.json' file.

        Returns:
            str: The hostname loaded from the 'settings.json' file.
        """
        return jmod.getvalue("hostname", "settings.json", "localhost", dt=app_settings)

    def parse(hostname):
        """
        Check if a hostname is valid.

        Args:
            hostname (str): The hostname to be checked.

        Returns:
            bool: True if the hostname is valid, False otherwise.
        """
        hostname = str(hostname)
        if hostname == "":
            return False            
        
        if hostname in ["localhost", "127.0.0.1", "0.0.0.0"]:
            return True # Allow localhost's
        # allow internal IPs
        if hostname.startswith("192.168.") or hostname.startswith("10.") or hostname.startswith("172."):
            return True
        
        if hostname.count(".") < 1 or hostname == "":
            return False
        allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-."
        char_filter = all(char in allowed_chars for char in hostname)
        if char_filter is False:
            return char_filter

    def setdomain(protocal='https'):
        """
        Sets the hostname for the application.

        This function prompts the user to enter a hostname and updates the 'hostname' value in the 'settings.json' file.

        Raises:
            KeyboardInterrupt: If the user cancels the operation.
            Exception: If an error occurs during the process.
        """
        from library.WebGUI.webgui import webgui_files
        try:
            hostname = pyhost_domain.get_via_input()
            jmod.setvalue(
                key="hostname",
                json_dir="settings.json",
                value=hostname,
                dt=app_settings
            )
            pylogger.info(f"Hostname set to {hostname}")
            print(f"Hostname set to {hostname}. Updating program...")

            if protocal == -1:
                tries = 0
                while True:
                    print("Which protocal would you like to use? (HTTPS or HTTP)")
                    protocal = input(">>> ")
                    if protocal.lower() in ["https", "http"]:
                        break
                    else:
                        if tries == 2:
                            print("Do you want us to pick for you? (y/n)")
                            pick = input(">>> ")
                            if pick.lower() in ["y", "yes"]:
                                if jmod.getvalue("webgui.localonly", "settings.json", True, dt=app_settings):
                                    protocal = "http"
                                else:
                                    protocal = "https"

                                print(f"Protocal set to {protocal}.")
                                break
                            else:
                                tries = 0
                                continue
                        tries += 1
                        print("Invalid protocal. Please try again.")
                        continue

            webgui_files.update_connection_details()
        except KeyboardInterrupt:
            print("Cancelled")
            exit()