import random
import random
import string
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
    "locked": False, # If the user is locked out of the account
    "api": {
        "logged_in": False,
    },
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

def generate_root_password():
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(16))
    return password
    

app_settings = {
    "do_autostart": True,
    "send_404_page": True,
    "first_launch": True,
    "do_autobackup": True,
    "backups_path": None, # The preferred backup path set by the user. defaults to something else depending on the OS
    "ssl_enabled": True,
    "api": {
        "running": False,
        "autoboot": False,
        "app_dir": "library.API.MainAPI",
        "port": 4045,
        "pid": None,
        "timeout_pid": None,
        "actionprint": False, # This prints all API actions to the console while active. Useful for debugging
    },
    "webgui": {
        "autoboot": False,
        "port": 4040, # No need for a pin as it requires a pyhost_user's login
        "pid": None,
        "silent": False,
    },
    # Hostname is used mainly in JS to connect to the API
    "hostname": -1, # Just the hostname, no port. -1 here to indicate the system should use localhost and ask the user for a default hostname    
    "ftpLogToFile": True,
    "FTP_Enabled": False,
    "FtpPort": 4035,
    "ftpAnonAllowed": False,
    "ftpRootPassword": generate_root_password(), # Password only resets if settings.json is deleted
    "pyhost_users": {}, # Should be a dict of dicts. Internal dicts being usernames as keys and their data as values
    "ftppid": None,
    "tokenMan": {
        "enabled": True,
        "expiration_hours": 24, # How long a session lasts in hours before expiring
        "pid": None,
    },
    "active_tokens": {},
}