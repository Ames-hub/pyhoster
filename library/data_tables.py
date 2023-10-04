from .application import application as app
def config_dt(app_name):
    '''Returns the DT for the config of an app. Needs an app_name to prevent autostarting multiple instances of the same app'''
    config_dt = {
        "name": app_name,
        "description": None,
        "autostart": True,
        "apptype": app.types.webpage(),
        "port": 80,
        "running": False,
        "boundpath": None, # Temporary. Updated on creation in create def
        "contentloc": f"instances/{app_name}/content/",
    }
    return config_dt