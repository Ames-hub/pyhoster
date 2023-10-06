config_dt = {
    "name": "defaultname", # Name of the app. Identifier
    "description": None,
    "autostart": True, # If the app should be started on startup
    "apptype": "WEBPAGE", # Used for potential future features such as not just being a website manager
    "port": 80, # Default port
    "running": False, # Used to check if an app is running that has the same port before starting it
    "pid": None, # pid is used for stopping the app
    "boundpath": None, # Temporary. Updated on creation in create def. Type: absolute path
    "contentloc": None,
    "index": "index.html",
    "restart_queued": False
}

app_settings = {
    "do_autostart": True,
    "send_404_page": True,
}