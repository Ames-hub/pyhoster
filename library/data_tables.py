from .application import application as app
import os
def config_dt(app_name):
    '''Returns the DT for the config of an app. Needs an app_name to prevent autostarting multiple instances of the same app'''
    config_dt = {
        "name": app_name,
        "description": None,
        "autostart": True,
        "apptype": app.types.webpage(), # Used for potential future features such as not just being a website manager
        "port": 80,
        "running": False, # Used to check if an app is running that has the same port before starting it
        "pid": None, # pid is used for stopping the app
        "boundpath": None, # Temporary. Updated on creation in create def. Type: absolute path
        "contentloc": os.path.abspath(f"instances/{app_name}/content/"),
    }
    return config_dt