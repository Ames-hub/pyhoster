import random
web_config_dt = {
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
    "last_updated": None,
    "404page": "404.html",
    "404page_enabled": False,
    "serve_default": True,
    # Security below here mostly
    "dir_listing": False,
    "do_securityheaders": True,
    "csp_directives": ["Content-Security-Policy", "default-src 'self';","script-src 'self';","style-src 'self';","img-src 'self';","font-src 'self'"], 
    "ssl_enabled": True,
    "warden": {
        "pages": [],
        "enabled": False,
        "pin": str(random.randint(100000,999999)), # random 6 digit pin
    },
}

new_user = {
    "username": None,
    "password": None,
    # Will be a dict with the app name as the key and the path as the value
    "ftp_dirs": {},
    "ftp_permissions": "elradfmw",
    "ftp_connected": False,
}

wsgi_config_dt = {
    "name": "defaultname",
    "description": None,
    "autostart": True,
    "apptype": "WSGI",
    "running": False,
    "port": 120,
    "pid": None,
    "boundpath": None,
    "last_updated": None,
}

# Generates a random password for the Root FTP user using cryptography
def generate_root_password():
    from cryptography.fernet import Fernet
    import base64
    key = Fernet.generate_key()
    f = Fernet(key)
    password = f.encrypt(b"password")
    password = base64.urlsafe_b64encode(password)
    password = password.decode("utf-8")
    del Fernet # Save memory.
    del base64 # Idk if it actually does anything other than make the variable inaccessible
    return password[0:16] # 16 is the max length of a password
    

app_settings = {
    "do_autostart": True,
    "send_404_page": True,
    "first_launch": True,
    "do_autobackup": True,
    "backups_path": None, # The preferred backup path set by the user. defaults to something else depending on the OS
    "ssl_enabled": True,
    "ftpLogToFile": True,
    "FTP_Enabled": False,
    "FtpPort": 789,
    "ftpAnonAllowed": False,
    "ftpRootPassword": generate_root_password(), # Password only resets if settings.json is deleted
    "pyhost_users": [], # Should be a list of dicts
    "ftppid": None,
}