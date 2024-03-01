# The following code is an API built with Quart for PyHost.
import os
import multiprocessing
import quart
from quart_cors import cors
from quart import request as quart_request
try:
    from ..userman import userman
    from ..instance import instance
    from ..warden import warden
    from ..jmod import jmod
    from ..data_tables import app_settings
except ImportError as err:
    print("Hello! To run Pyhost, you must run the file pyhost.py located in this projects root directory, not this file.\nThank you!")
    from library.pylog import pylog
    pylog().error(f"Import error in {__name__}", err)

from ..pylog import pylog
logapi = pylog(
    filename='logs/api/%TIMENOW%.log', # Save in its own folder. Its a bit spammy if you have a lot of API requests or people leaving the webgui open
    logform="%loglevel% - %time% %H:%M:%S - %file% | " # Being more specific as this is the API
)
logapi.info("API File Initialized.")

app = quart.Quart(__name__)
# app = cors(app, allow_origin="*", allow_methods=["POST", "OPTIONS"], allow_headers=["Content-Type"])

def apiprint(msg):
    actionprint = jmod.getvalue("api.actionprint", "settings.json", False, app_settings)
    if actionprint:
        print(msg)
        logapi.info(msg)
    else:
        logapi.info(msg)

# Note: When in doubt, blame this function. Especially if nothing API related is working. 
def prechecks(func):
    async def wrapper(*args, **kwargs):
        ip_address = quart_request.remote_addr
        logapi.info(f"IP Address: {ip_address}, Function: {func.__name__}, Arguments: {args, kwargs}")
        # Gets the data from the POST request
        data = await quart_request.get_json()

        token = data.get('token', None)
        if token is None:
            return {'status': 'no token'}, 400
        
        valid_session = userman.session.validate_session(token, ip_address)
        if not valid_session == True:
            return {'status': 'invalid token'}, 401

        return await func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@app.route('/', methods=['POST'])
@prechecks
async def index():
    return {'status': 'ok'}, 200

@app.route('/instances/start', methods=['POST', 'OPTIONS'])
@prechecks
async def start_app():
    if quart.request.method == 'OPTIONS':
        # Handling CORS preflight request
        response = quart.Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    # Rest of your code for handling POST requests
    data = await quart.request.get_json()
    try:
        app_name = data['app_name']
    except KeyError:
        return 'Please provide an app_name in the POST data', 400

    apiprint(f"API/Remote user {userman.session.get_user(data['token'])} requested to start app \"{app_name}\". Working...")
    multiprocessing.Process(
        target=instance.start_interface, args=(app_name, False)
    ).start()
    return {"status": 200}

@app.route('/instances/stop', methods=['POST'])
@prechecks
async def stop_app():
    # Gets the data from the POST request
    data = await quart.request.get_json()
    try:
        app_name = data['app_name']
    except KeyError:
        return 'Please provide an app_name in the POST data', 400

    apiprint(f"API/Remote user {userman.session.get_user(data['token'])} requested to stop app \"{app_name}\". Working...")
    instance.stop(app_name, False)
    return {"status": 200}

@app.route('/instances/webcreate', methods=['POST'])
@prechecks
async def webcreate():
    # Gets the data from the POST request
    data = await quart.request.get_json()
    try:
        app_name = str(data['app_name'])
        port = int(data['port'])
        do_autostart = bool(data['do_autostart'])
        
        # Optional data
        app_desc = str(data.get('app_desc', None))
        boundpath = str(data.get('boundpath', "internal"))
    except KeyError:
        return {"msg":'Please provide an *app_name, *port, *do_autostart, app_desc, boundpath in the POST data'}, 400
    except TypeError:
        return {"msg":'Please provide an *app_name (str), *port (int), *do_autostart (bool), app_desc (str), boundpath (str) in the POST data'}, 400
    except ValueError:
        return {"msg":'Please provide an *app_name, *port, *do_autostart, app_desc, boundpath in the POST data'}, 400

    if " " in app_name:
        return {"msg": "Name cannot contain spaces"}, 400

    apiprint(f"API/Remote user {userman.session.get_user(data['token'])} requested to create app \"{app_name}\". Working...")
    instance.create_web(
        app_name=app_name,
        app_desc=app_desc,
        port=port,
        boundpath=boundpath,
        do_autostart=do_autostart,
        is_interface=False
    )
    return {"msg":"Successful"}, 200

@app.route('/instances/delete', methods=['POST'])
@prechecks
async def webdelete():
    if quart.request.method == 'POST':
        # Gets the data from the POST request
        data = await quart.request.get_json()
        try:
            app_name = data['app_name']
            del_backups = data.get('del_backups', False)
        except KeyError:
            return 'Please provide an app_name in the POST data', 400

        apiprint(f"API/Remote user {userman.session.get_user(data['token'])} requested to delete app \"{app_name}\". Working...")
        instance.delete(app_name, is_interface=False, ask_confirmation=False, del_backups=del_backups)
        return {"status": 200}

@app.route('/instances/getstatus', methods=['POST'])
@prechecks
async def get_status():
    if quart.request.method == 'POST':
        # Gets the data from the POST request
        data = await quart.request.get_json()
        try:
            app_name = data['app_name']
        except KeyError:
            return 'Please provide an app_name in the POST data', 400

        apiprint(f"API/Remote user {userman.session.get_user(data['token'])} requested to get status of app \"{app_name}\". Working...")
        status = instance.get_status(app_name)
        return status, 200

@app.route("/instances/getall", methods=['POST'])
@prechecks
async def get_all():
    if quart.request.method == 'POST':
        '''Returns all status's for all apps'''
        # Gets the data from the POST request
        data = await quart.request.get_json()
        apiprint(f"API/Remote user {userman.session.get_user(data['token'])} requested to get status of all apps. Working...")
        status_dict = {}
        for app in os.listdir('instances/'):
            status = instance.get_status(app, is_interface=False)
            status_dict[app] = status
        return status_dict, 200
    
@app.route('/warden/getstatus', methods=['POST'])
@prechecks
async def get_warden_status():
    if quart.request.method == 'POST':
        # Gets the data from the POST request
        data = await quart.request.get_json()
        try:
            app_name = str(data['app_name'])
        except KeyError:
            return 'Please provide an app_name in the POST data', 400

        apiprint(f"API/Remote user {userman.session.get_user(data['token'])} requested to get Warden status. Working...")
        status = warden.get_status(app_name)
        return {"status": status}

# @app.route('/userman/login', methods=['OPTIONS'])
# async def login_options():
#     # Handling CORS preflight request
#     response = quart.Response()
#     response.headers['Access-Control-Allow-Origin'] = '*'
#     response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
#     response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
#     return response
@app.route('/userman/login', methods=['POST'])
async def login():
    data = await quart.request.get_json()
    try:
        username = str(data['username'])
        password = str(data['password'])
    except KeyError:
        return 'Please provide a username and password in the POST data', 400
    except TypeError:
        return 'Please provide a username (str) and password (str) in the POST data', 400
    
    apiprint(f"API/Remote user {data['username']} requested to login. Working...")
    session = userman.session(username, password, IP_Address=quart.request.remote_addr)
    status = session.htmlstatus
    return {"status": status, "session": session.token}
