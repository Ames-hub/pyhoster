# A custom logging function. Built this because normal logging library occassionally is a pain
import multiprocessing
import traceback
import datetime
import inspect
import random
import os

log_queue = multiprocessing.Queue()
priority_queue = multiprocessing.Queue()
logIDs = {}

class pylog:
    """
    A logging utility class for writing log messages to a file.
    Built especially for multi-threaded applications or applications with multiple files that all want to log to the same file.

    # GETTING STARTED
    1. From pylog file, import logman and run it in a separate thread. (If you don't do this, your logs will not be written to the file)
    2. From pylog file, import pylog
    3. Create a pylog object. Eg,
    >>> logger = pylog(
    >>>     filename='logs/application.log',
    >>> # Where it is saved and what it is called
    >>>     logform='%loglevel% - %(time)s | '
    >>> )
    >>> # A Formatted prefix to every log message
    4. Create a LogMan thread and run it. Eg,
    >>> from pylog import logman
    >>> import multiprocessing
    >>> logman_thread = multiprocessing.Process(target=logman, args=())
    >>> logman_thread.start()
    5. Start logging! Eg,
    >>> logger.info('Hello World!')

    Args:
        filename (str): The name of the log file. Defaults to 'logs/%TIMENOW%.log'.
        logform (str): The log message format. Defaults to '%loglevel% - %(time)s - %(file)s | '.
        uselatest (bool): Whether to create a 'latest.log' file before renaming on next session. Defaults to True.

    Attributes:
        filename (str): The name of the log file.
        logform (str): The log message format.

    """

    def __init__(self, 
        filename:str='logs/%TIMENOW%.log',
        logform:str='%loglevel% - %time% - %files | ',
        # Uselatest is in development. Not recommended to use.
        uselatest:bool=False,
        ):
        if not filename.endswith('.log'):
            filename += '.log'

        datenow = datetime.datetime.now().strftime("%Y-%m-%d, %I%p")
        if '%TIMENOW%' in filename:
            filename = filename.replace('%TIMENOW%', datenow)

        self.filename = filename
        self.logform = logform
        self.uselatest = uselatest
        logdirectory = os.path.dirname(self.filename)
        os.makedirs(logdirectory, exist_ok=True)

        # On the next startup, rename the latest.log to what's saved in that file.
        self.identifier = str(random.randint(1, 9999999))
        self.latest_log_path = os.path.join(os.path.dirname(self.filename), "latest.log")
        logIDs[self.identifier] = {
            "uselatest": self.uselatest,
            "latest_log_path": self.latest_log_path
        }

    def info(self, message):
        """
        Logs an informational message.

        Args:
            message (str): The message to be logged.

        """
        logform = self.parse_logform(self.levels.INFO)
        message = f'{logform}{message}'
        self.queue_in(message)

    def warning(self, message):
        """
        Logs a warning message.

        Args:
            message (str): The message to be logged.

        """
        logform = self.parse_logform(self.levels.WARNING)
        message = f'{logform}{message}'
        self.queue_in(message)

    def error(self, message, exception: Exception):
        """
        Logs an error message along with the exception details.

        Args:
            message (str): The error message to be logged.
            exception (Exception): The exception object.

        """
        logform = self.parse_logform(self.levels.ERROR)
        message = f'{logform}{message}\n{exception}\n{traceback.format_exc()}'
        self.queue_in(message)

    def debug(self, message):
        """
        Logs a debug message.

        Args:
            message (str): The message to be logged.

        """
        logform = self.parse_logform(self.levels.DEBUG)
        message = f'{logform}{message}'
        self.queue_in(message, debug=True)

    def queue_in(self, message, debug=False):
        if not debug:
            log_queue.put({"msg": message, "directory": self.filename, "identifier": self.identifier})
        else:
            priority_queue.put({"msg": message, "directory": self.filename, "identifier": self.identifier})

    def parse_logform(self, loglevel):
        """
        Parses the log message format and replaces placeholders with actual values.

        Args:
            loglevel (str): The log level.

        Returns:
            str: The parsed log message format.

        """
        logform = self.logform
        logform = logform.replace('%loglevel%', loglevel)
        logform = logform.replace('%day%', datetime.datetime.now().strftime("%Y-%m-%d"))
        logform = logform.replace('%time%', datetime.datetime.now().strftime("%H:%M:%S"))
        # Gets the lineno of the caller and the file name
        logform = logform.replace('%files', f'{inspect.stack()[2][1]}:{inspect.stack()[2][2]}')
        return logform

    class levels:
        # Log levels
        DEBUG = "DEBUG"
        INFO = "INFO"
        WARNING = "WARNING"
        ERROR = "ERROR"

def logman():
    '''
    Worker that writes logs to file from the Queue.

    Only run this function once and ensure it is only ran once. If it is not ran only once, your logs will be overwritten
    IF you have multiple threads/files running this function. 
    '''
    def writer():
        if priority_queue.qsize() == 0:
            log = log_queue.get()
        else:
            log = priority_queue.get()
        try:
            make_at = os.path.dirname(log['directory'])
            latest_log = os.path.join(make_at, "latest.log")
            timeset_dir = os.path.join(make_at, "timeset")
            
            if logIDs[log['identifier']]['uselatest'] == False:
                os.makedirs(os.path.dirname(log['directory']), exist_ok=True)
                with open(log['directory'], 'a+') as f:
                    f.write(log['msg'] + '\n')
            else:
                # If latest log doesn't exist, make it and the file dictating what time it was made.
                if not os.path.exists(latest_log):
                    with open(latest_log, 'w+') as f:
                        f.write("")  # Just create an empty latest.log for now
                    with open(timeset_dir, 'w+') as f:
                        f.write(str(datetime.datetime.now().strftime("%Y-%m-%d, %I%p")))
                
                # Check if there's a timeset file, and if so, use it to rename latest.log
                if os.path.exists(timeset_dir):
                    with open(timeset_dir, 'r') as f:
                        timestamp = f.read().strip()
                    new_filename = os.path.join(make_at, f"{timestamp}.log")
                    os.rename(latest_log, new_filename)

                with open(latest_log, 'a+') as f:
                    f.write(log['msg'] + '\n')
        except (PermissionError, OSError) as err:
            # Handle errors appropriately
            err_formatted = traceback.format_exc()
            err_log_msg = f'I encountered an error while logging the following message\n\"{log["msg"]}\"\nMy Error: {err}\n{err_formatted}'
            with open('pylog_error.log', 'a+') as f:
                f.write(err_log_msg)

    try:
        while True:
            writer()
    except KeyboardInterrupt:
        print("...\nWaiting for logs to be written to file...")
        log_queue.close()
        while log_queue.qsize() > 0:
            writer()
        print("Done writing logs to file.")