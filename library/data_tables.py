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

# TODO Implement the "locked out" thing everywhere
new_user = {
    "username": None,
    "password": None,
    "locked": False, # If the user is locked out of the account
    "api": {
        "logged_in": False,
        "token": None,
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
        "port": 987,
        "pid": None,
        "timeout_pid": None,
    },
    "webgui": {
        "autoboot": False,
        "port": 4040, # No need for a pin as it requires a pyhost_user's login
        "pid": None,
        "silent": False,
        "hostname": "localhost", # Just the hostname, no port (eg, example.com or 192.168.0.190)
    },
    "ftpLogToFile": True,
    "FTP_Enabled": False,
    "FtpPort": 789,
    "ftpAnonAllowed": False,
    "ftpRootPassword": generate_root_password(), # Password only resets if settings.json is deleted
    "pyhost_users": {}, # Should be a dict of dicts. Internal dicts being usernames as keys and their data as values
    "ftppid": None,
}