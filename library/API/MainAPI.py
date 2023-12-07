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