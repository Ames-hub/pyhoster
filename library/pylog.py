# A custom logging function. Built this because normal logging library occassionally is a pain
import multiprocessing
import traceback
import datetime
import inspect
import os

log_queue = multiprocessing.Queue()

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
    
    Args:
        filename (str): The name of the log file. Defaults to 'logs/%TIMENOW%.log'.
        logform (str): The log message format. Defaults to '%loglevel% - %(time)s - %(file)s | '.

    Attributes:
        filename (str): The name of the log file.
        logform (str): The log message format.

    """

    def __init__(self, 
        filename='logs/%TIMENOW%.log',
        logform='%loglevel% - %(time)s - %(file)s | ',
        ):
        if not filename.endswith('.log'):
            filename += '.log'

        if '%TIMENOW%' in filename:
            filename = filename.replace('%TIMENOW%', datetime.datetime.now().strftime("%Y-%b-%d at %l:%m%p"))

        self.filename = filename
        self.logform = logform

    def info(self, message):
        """
        Logs an informational message.

        Args:
            message (str): The message to be logged.

        """
        logform = self.parse_logform(self.levels.INFO)
        message = f'{logform}{message}'
        log_queue.put({"msg": message, "directory": self.filename})

    def warning(self, message):
        """
        Logs a warning message.

        Args:
            message (str): The message to be logged.

        """
        logform = self.parse_logform(self.levels.WARNING)
        message = f'{logform}{message}'
        log_queue.put({"msg": message, "directory": self.filename})

    def error(self, message, exception: Exception):
        """
        Logs an error message along with the exception details.

        Args:
            message (str): The error message to be logged.
            exception (Exception): The exception object.

        """
        logform = self.parse_logform(self.levels.ERROR)
        message = f'{logform}{message}\n{exception}\n{traceback.format_exc()}'
        log_queue.put({"msg": message, "directory": self.filename})

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
        logform = logform.replace('%(time)s', datetime.datetime.now().strftime("%Y-%b-%d at %l:%m%p"))
        # Gets the lineno of the caller and the file name
        logform = logform.replace('%(file)s', f'{inspect.stack()[2][1]}:{inspect.stack()[2][2]}')
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
    def chunk_searcher(chunk, search_for):
        '''
        Searches a chunk of text for a string. Returns True if found, False if not.
        '''
        try:
            if search_for in chunk:
                return True
            else:
                return False
        except KeyboardInterrupt:
            return -1 # Exit gracefully

    try:
        while True:
            log = log_queue.get()
            try:
                os.makedirs(os.path.dirname(log['directory']), exist_ok=True)
                with open(log['directory'], 'a+') as f:
                    f.write(log['msg'] + '\n')
            except (PermissionError, OSError) as err:
                # Open a log file in the current directory (which it DOES have permission to write to)
                err_formatted = traceback.format_exc()
                err_log_msg = f'I encountered an error while logging the following message\n\"{log["msg"]}\"\nMy Error: {err}\n{err_formatted}'
                with open('pylog_error.log', 'r+') as f:
                    content = f.read()
                if len(content) < 100_000:
                    if err_log_msg not in content: # Doesn't write the same error twice
                        with open('pylog_error.log', 'a+') as f:
                            f.write(err_log_msg)
                else:
                    # Start threads, break the content into chunks, hand each thread a chunk and let them search through it for the content
                    threads = []
                    content = content.splitlines()
                    for i in range(3):
                        chunk = content[i * 1000 : (i + 1) * 1000]
                        thread = multiprocessing.Process(
                            target=chunk_searcher,
                            args=(chunk, err_log_msg)
                        )
                        threads.append(thread)
                    
                    for thread in threads:
                        thread: multiprocessing.Process
                        thread.start()

                    for thread in threads:
                        if thread.is_alive():
                            thread.join() # Wait for the thread to finish
                        
                        result = thread.exitcode
                        if result == True:
                            break # Found the error in the log file, no need to write it again
                        elif result == -1: # Exit gracefully since the user pressed Ctrl+C
                            return True
                    else: # Else doesn't run if the for loop is broken out of.
                        # Didn't find the error in the log file, write it
                        with open('pylog_error.log', 'a+') as f:
                            f.write(err_log_msg)

    except KeyboardInterrupt:
        return True # Exit gracefully
