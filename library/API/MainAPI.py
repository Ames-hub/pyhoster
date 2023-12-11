# The following code is an API built with Flask for PyHost.
from flask import request
import os
import logging, multiprocessing, flask
from library.userman import userman
from library.instance import instance
from library.warden import warden

app = flask.Flask(__name__)

def prechecks(func):
    def wrapper(*args, **kwargs):
        ip_address = request.remote_addr
        logging.info(f"IP Address: {ip_address}, Function: {func.__name__}, Arguments: {args, kwargs}")
        # Gets the data from the POST request
        data = dict(request.get_json())

        username = data.get('username')
        password = data.get('password')
        if username is None or password is None:
            return 'Bad Request. In the POST data, please provide a "username" and "password"', 400
        allowed = userman.api.login(username=username, password=password)
        if not allowed:
            return 'Unauthorized. In the POST data, please provide a valid "username" and "password"', 401

        try:
            if userman.is_locked(username):
                return 'Unauthorized. Your account is locked.', 401
        except userman.errors.UserDoesNotExist:
            return f'User "{username}" does not exist.', 404

        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@app.route('/', methods=['POST'])
@prechecks
def index():
    return 'Pong!', 200

@app.route('/instances/start', methods=['POST'])
@prechecks
def start_app():
    # Gets the data from the POST request
    data = dict(request.get_json())
    try:
        app_name = data['app_name']
    except KeyError:
        return 'Please provide an app_name in the POST data', 400

    print(f"API/Remote user {data['username']} requested to start app \"{app_name}\". Complying...")
    multiprocessing.Process(
        target=instance.start_interface, args=(app_name, False)
    ).start()
    logging.info(
        f"API/Remote user {data['username']} requested to start app \"{app_name}\". Complying..."
    )
    return {"status": 200}

@app.route('/instances/stop', methods=['POST'])
@prechecks
def stop_app():
    # Gets the data from the POST request
    data = dict(request.get_json())
    try:
        app_name = data['app_name']
    except KeyError:
        return 'Please provide an app_name in the POST data', 400

    print(f"API/Remote user {data['username']} requested to stop app \"{app_name}\". Complying...")
    instance.stop(app_name)
    logging.info(
        f"API/Remote user {data['username']} requested to stop app \"{app_name}\". Complying..."
    )
    return {"status": 200}

@app.route('/instances/webcreate', methods=['POST'])
@prechecks
def webcreate():
    # Gets the data from the POST request
    data = dict(request.get_json())
    try:
        app_name = str(data['app_name'])
        app_desc = str(data['app_desc'])
        port = int(data['port'])
        boundpath = str(data['boundpath'])
        do_autostart = bool(data['do_autostart'])
    except KeyError:
        return 'Please provide an app_name, app_desc, port, boundpath, do_autostart in the POST data', 400
    except TypeError:
        return 'Please provide an app_name (str), app_desc (str), port (int), boundpath (str), do_autostart (bool) in the POST data', 400
    except ValueError:
        return 'Please provide an app_name, app_desc, port, boundpath, do_autostart in the POST data', 400

    print(f"API/Remote user {data['username']} requested to create app \"{app_name}\". Complying...")
    instance.create_web(
        app_name=app_name,
        app_desc=app_desc,
        port=port,
        boundpath=boundpath,
        do_autostart=do_autostart,
        )
    logging.info(
        f"API/Remote user {data['username']} requested to create app \"{app_name}\". Complying..."
    )
    return {"status": 200}

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

    print(f"API/Remote user {data['username']} requested to delete app \"{app_name}\". Complying...")
    instance.delete(app_name, is_interface=False, ask_confirmation=False, del_backups=del_backups)
    logging.info(
        f"API/Remote user {data['username']} requested to delete app \"{app_name}\". Complying..."
    )
    return {"status": 200}

@app.route('/instances/getstatus', methods=['POST'])
@prechecks
def get_status():
    # Gets the data from the POST request
    data = dict(request.get_json())
    try:
        app_name = data['app_name']
    except KeyError:
        return 'Please provide an app_name in the POST data', 400

    print(f"API/Remote user {data['username']} requested to get status of app \"{app_name}\". Complying...")
    status = instance.get_status(app_name)
    logging.info(
        f"API/Remote user {data['username']} requested to get status of app \"{app_name}\". Complying..."
    )
    return status, 200

@app.route("/instances/getall", methods=['POST'])
@prechecks
def get_all():
    '''Returns all status's for all apps'''
    # Gets the data from the POST request
    data = dict(request.get_json())
    print(f"API/Remote user {data['username']} requested to get status of all apps. Complying...")
    status_dict = {}
    for app in os.listdir('instances/'):
        status = instance.get_status(app)
        status_dict[app] = status

    logging.info(
        f"API/Remote user {data['username']} requested to get status of all apps. Complying..."
    )
    return status_dict, 200

# TODO: Test if these work
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

    print(f"API/Remote user {data['username']} requested to set Warden status to \"{status}\" for app \"{app_name}\". Complying...")
    warden.set_status(app_name, status)
    logging.info(
        f"API/Remote user {data['username']} requested to set Warden status to \"{status}\" for app \"{app_name}\". Complying..."
    )
    return {"status": 200}

@app.route('/warden/getstatus', methods=['POST'])
@prechecks
def get_warden_status():
    # Gets the data from the POST request
    data = dict(request.get_json())
    try:
        app_name = str(data['app_name'])
    except KeyError:
        return 'Please provide an app_name in the POST data', 400

    print(f"API/Remote user {data['username']} requested to get Warden status. Complying...")
    status = warden.get_status(app_name)
    logging.info(
        f"API/Remote user {data['username']} requested to get Warden status. Complying..."
    )
    return {"status": status}

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

    print(f"API/Remote user {data['username']} requested to add Warden page \"{page_name}\". Complying...")
    msg = warden.add_page(app_name=app_name, page_dir=page_name, is_interface=False)
    logging.info(
        f"API/Remote user {data['username']} requested to add Warden page \"{page_name}\". Complying..."
    )
    # Uses match to check if the message is a success or failure and determine a html code
    answers = {
        "Page added.": 200,
        "Page already exists.": 400,
        "App does not exist.": 400,
    }
    status = answers.get(msg, 400)

    return {"status": msg}, status

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

    print(f"API/Remote user {data['username']} requested to delete Warden page \"{page_dir}\". Complying...")
    msg = warden.rem_page(app_name=app_name, page_dir=page_dir, is_interface=False)
    logging.info(
        f"API/Remote user {data['username']} requested to delete Warden page \"{page_dir}\". Complying..."
    )
    status = 200 if msg == "Page removed." else 400
    return {"status": msg}, status

# TODO: Add a route(s) to control the FTP server
# TODO: Add a route(s) to control the User Manager