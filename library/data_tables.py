from .application import application as app
def config_dt(app_name):
    '''Returns the DT for the config of an app. Needs an app_name to prevent autostarting multiple instances of the same app'''
    config_dt = {
        "name": app_name,
        "description": None,
        app_name: { # Includes appname to prevent autostarting multiple instances of the same app
            "autostart": True,
            "apptype": app.types.webpage,
            "port": 8080,
            "boundpath": f"instances/{app_name}/",
        }
    }
    return config_dt