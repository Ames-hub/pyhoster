# The following code is an API built with Flask for PyHost.
from flask import request
import logging, multiprocessing, flask
from library.userman import userman
from library.instance import instance

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
        else:
            return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@app.route('/', methods=['POST'])
@prechecks
def index():
    return 'Pong!', 200

@app.route('/start_app', methods=['POST'])
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

@app.route('/stop_app', methods=['POST'])
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

@app.route('/webcreate', methods=['POST'])
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

@app.route('/delete_app', methods=['POST'])
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

# TODO: Add a route for getting the status of an app
# TODO: Add a route(s) to control Warden
# TODO: Add a route(s) to control the FTP server
# TODO: Add a route(s) to control the User Manager