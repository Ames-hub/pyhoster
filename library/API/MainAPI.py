# The following code is an API built with Flask for PyHost.
from flask import request
import os
import multiprocessing, flask
from flask_cors import CORS
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
    logform="%loglevel% - %time% %H:%M:%S - %file% | " # Being more specific as this is the API
)# filename='logs/api/%TIMENOW%.log')
logapi.info("API File Initialized.")

app = flask.Flask(__name__)
CORS(app, origins='*') #TODO: I'll improve this when I can give a damn

def apiprint(msg):
    actionprint = jmod.getvalue("api.actionprint", "settings.json", False, app_settings)
    if actionprint:
        print(msg)
        logapi.info(msg)
    else:
        logapi.info(msg)

def prechecks(func):
    def wrapper(*args, **kwargs):
        ip_address = request.remote_addr
        logapi.info(f"IP Address: {ip_address}, Function: {func.__name__}, Arguments: {args, kwargs}")
        # Gets the data from the POST request
        data = dict(request.get_json())

        token = data.get('token', None)
        if token is None:
            return {'status': 'no token'}, 400
        
        valid_session = userman.session.validate_session(token, ip_address)
        if not valid_session == True:
            return {'status': 'invalid token'}, 401

        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@app.route('/', methods=['POST'])
@prechecks
def index():
    return {'status': 'ok'}, 200

@app.route('/instances/start/', methods=['OPTIONS'])
def startoptions():
    response = flask.Response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response
@app.route('/instances/start', methods=['POST'])
@prechecks
def start_app():
    # Gets the data from the POST request
    data = dict(request.get_json())
    try:
        app_name = data['app_name']
    except KeyError:
        return 'Please provide an app_name in the POST data', 400

    apiprint(f"API/Remote user {userman.session.get_user(data['token'])} requested to start app \"{app_name}\". Working...")
    multiprocessing.Process(
        target=instance.start_interface, args=(app_name, False)
    ).start()
    return {"status": 200}

@app.route('/instances/stop/', methods=['OPTIONS'])
def stopoptions():
    response = flask.Response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response
@app.route('/instances/stop', methods=['POST'])
@prechecks
def stop_app():
    # Gets the data from the POST request
    data = dict(request.get_json())
    try:
        app_name = data['app_name']
    except KeyError:
        return 'Please provide an app_name in the POST data', 400

    apiprint(f"API/Remote user {userman.session.get_user(data['token'])} requested to stop app \"{app_name}\". Working...")
    instance.stop(app_name, False)
    return {"status": 200}

@app.route('/instances/webcreate/', methods=['OPTIONS'])
def wcreateoptions():
    response = flask.Response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response
@app.route('/instances/webcreate', methods=['POST'])
@prechecks
def webcreate():
    # Gets the data from the POST request
    data = dict(request.get_json())
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

@app.route('/instances/delete/', methods=['OPTIONS'])
def deleteoptions():
    response = flask.Response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response
@app.route('/instances/delete', methods=['POST'])
@prechecks
def webdelete():
    # Gets the data from the POST request
    data = dict(request.get_json())
    try:
        app_name = data['app_name']
        del_backups = data.get('del_backups', False)
    except KeyError:
        return 'Please provide an app_name in the POST data', 400

    apiprint(f"API/Remote user {userman.session.get_user(data['token'])} requested to delete app \"{app_name}\". Working...")
    instance.delete(app_name, is_interface=False, ask_confirmation=False, del_backups=del_backups)
    return {"status": 200}

@app.route('/instances/delete/', methods=['OPTIONS'])
def statusgetoptions():
    response = flask.Response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response
@app.route('/instances/getstatus', methods=['POST'])
@prechecks
def get_status():
    # Gets the data from the POST request
    data = dict(request.get_json())
    try:
        app_name = data['app_name']
    except KeyError:
        return 'Please provide an app_name in the POST data', 400

    apiprint(f"API/Remote user {userman.session.get_user(data['token'])} requested to get status of app \"{app_name}\". Working...")
    status = instance.get_status(app_name)
    return status, 200

@app.route('/instances/getall/', methods=['OPTIONS'])
def GetAllStatusesOptions():
    response = flask.Response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response
@app.route("/instances/getall", methods=['POST'])
@prechecks
def get_all():
    '''Returns all status's for all apps'''
    # Gets the data from the POST request
    data = dict(request.get_json())
    apiprint(f"API/Remote user {userman.session.get_user(data['token'])} requested to get status of all apps. Working...")
    status_dict = {}
    for app in os.listdir('instances/'):
        status = instance.get_status(app, is_interface=False)
        status_dict[app] = status
    return status_dict, 200

@app.route('/warden/setstatus/', methods=['OPTIONS'])
def wardenoptions1():
    response = flask.Response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response
@app.route('/warden/setstatus', methods=['POST'])
@prechecks
def set_warden_status():
    # Gets the data from the POST request
    data = dict(request.get_json())
    try:
        status = bool(data['status'])
        app_name = str(data['app_name'])
    except KeyError:
        return 'Please provide a status and app_name in the POST data', 400
    except TypeError:
        return 'Please provide a status (bool) and app_name (str) in the POST data', 400

    apiprint(f"API/Remote user {userman.session.get_user(data['token'])} requested to set Warden status to \"{status}\" for app \"{app_name}\". Working...")
    warden.set_status(app_name, status)
    return {"status": 200}

@app.route('/warden/getstatus/', methods=['OPTIONS'])
def wardenoptions2():
    response = flask.Response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response
@app.route('/warden/getstatus', methods=['POST'])
@prechecks
def get_warden_status():
    # Gets the data from the POST request
    data = dict(request.get_json())
    try:
        app_name = str(data['app_name'])
    except KeyError:
        return 'Please provide an app_name in the POST data', 400

    apiprint(f"API/Remote user {userman.session.get_user(data['token'])} requested to get Warden status. Working...")
    status = warden.get_status(app_name)
    return {"status": status}

@app.route('/warden/addpage/', methods=['OPTIONS'])
def wardenoptions3():
    response = flask.Response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response
@app.route('/warden/addpage', methods=['POST'])
@prechecks
def add_warden_page():
    # Gets the data from the POST request
    data = dict(request.get_json())
    try:
        app_name = str(data['app_name'])
        if app_name == "Brew Tea":
            status = 418 # LOL
            msg = "Am Tea bot :) ... Fr tho your command did nothing"
            return {"status": msg}, status

        page_name = str(data['page_dir'])
    except KeyError:
        return 'Please provide an app_name, page_dir (str. eg, "index.html" or contentdir/subdir/page.html) in the POST data', 400
    except TypeError:
        return 'Please provide an app_name (str), page_dir (str. eg, "index.html" or contentdir/subdir/page.html) in the POST data', 400

    apiprint(f"API/Remote user {userman.session.get_user(data['token'])} requested to add Warden page \"{page_name}\". Working...")
    msg = warden.add_page(app_name=app_name, page_dir=page_name, is_interface=False)
    # Uses match to check if the message is a success or failure and determine a html code
    answers = {
        "Page added.": 200,
        "Page already exists.": 400,
        "App does not exist.": 400,
    }
    status = answers.get(msg, 400)

    return {"status": msg}, status

@app.route('/warden/rempage/', methods=['OPTIONS'])
def wardenoptions4():
    response = flask.Response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response
@app.route('/warden/rempage', methods=['POST'])
@prechecks
def delete_warden_page():
    # Gets the data from the POST request
    data = dict(request.get_json())
    try:
        app_name = str(data['app_name'])
        page_dir = str(data['page_dir'])
    except KeyError:
        return 'Please provide an app_name and page_dir (str. eg, "index.html" or contentdir/subdir/page.html) in the POST data', 400
    except TypeError:
        return 'Please provide an app_name (str) and page_dir (str. eg, "index.html" or contentdir/subdir/page.html) in the POST data', 400

    apiprint(f"API/Remote user {userman.session.get_user(data['token'])} requested to delete Warden page \"{page_dir}\". Working...")
    msg = warden.rem_page(app_name=app_name, page_dir=page_dir, is_interface=False)
    status = 200 if msg == "Page removed." else 400
    return {"status": msg}, status

# TODO: Add a route(s) to control the FTP server
# TODO: Add a route(s) to control the User Manager

@app.route('/userman/login/', methods=['OPTIONS'])
def usermanoptions1():
    response = flask.Response()
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS, GET'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response
@app.route('/userman/login', methods=['POST'])
def login():
    # Gets the data from the POST request
    data = dict(request.get_json())
    try:
        username = str(data['username'])
        password = str(data['password'])
    except KeyError:
        return 'Please provide a username and password in the POST data', 400
    except TypeError:
        return 'Please provide a username (str) and password (str) in the POST data', 400

    apiprint(f"API/Remote user {data['username']} requested to login. Working...")
    session = userman.session(username, password, IP_Address=request.remote_addr)
    status = session.htmlstatus
    return {"status": status, "session": session.token}
