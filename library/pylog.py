# Pylog is a Custom Logging Library for PyHost (specifically) but can be used for any python project.
# It is built for when multiple files/functions need to log to the same file at the same time. Standard logging library poorly handles this.
# Pylog is built to be threading safe and multiprocessing safe and handle the stress.
import multiprocessing
import traceback
import datetime
import inspect
import random
import json
import time
import os

global_cachedir = os.path.join(os.getcwd(), "logs/.cache/")

cacheitem_data_table = {
    "msg": None,
    "exception": None,
    "priority": None,
    "directory": None,
}

class logQueue:
    def __init__(self, cachedir) -> None:
        self.cachedir = cachedir
        self.priority_closed = False
        self.normal_closed = False

    def is_empty(self, queue_type):
        """
        Check if a directory is empty based on the specified queue type.

        Args:
            queue_type (str): The queue type to consider ('priority', 'normal', or 'both').

        Returns:
            bool: True if the directory is empty for the specified queue type, False otherwise.
        """
        directory = self.cachedir
        # Get the list of files in the directory
        cache = os.listdir(directory)

        if queue_type == "both":
            if len(cache) == 0:
                return True
            else:
                return False

        # Iterate over each file in the directory
        for item in cache:
            # Open the file
            with open(os.path.join(directory, item), 'r') as f:
                try:
                    # Load the JSON data from the file
                    item_queue_type = json.load(f)['priority']
                except json.JSONDecodeError:
                    # Skip the file if it is not a valid JSON
                    continue

                # Check if the queue type matches the item's queue type
                if queue_type == "priority" and item_queue_type is True:
                    return False
                elif queue_type == "normal" and item_queue_type is False:
                    return False

        # Return True if no matching items found
        return True

    def close(self, priority=False):
        if priority:
            self.priority_closed = True
        else:
            self.normal_closed = True

    def open(self, priority=False):
        if priority:
            self.priority_closed = False
        else:
            self.normal_closed = False

    def get(self, priority=False):
        """
        Retrieve data from the cache directory.

        Args:
            priority (bool, optional): If True, retrieve data with priority. Defaults to False.

        Returns:
            dict: The retrieved data from the cache directory.
        """
        # Get the list of files in the cache directory
        cache = os.listdir(self.cachedir)

        # Create a dictionary to store the queue numbers and corresponding items
        numbers = {}

        # Iterate over each item in the cache directory
        for item in cache:
            with open(os.path.join(self.cachedir, item), 'r') as f:
                try:
                    item_priority = json.load(f)['priority']
                except json.JSONDecodeError:
                    continue

                # If priority is True and item_priority is True, retrieve the item with highest priority
                if priority is True and item_priority is True:
                    number = self.get_queue_number(item)
                    numbers[number] = item
                    break

            # Retrieve the queue number for the item
            number = self.get_queue_number(item)
            numbers[number] = item

        # Get the item with the minimum queue number
        try:
            item = numbers[min(numbers.keys())]
        except ValueError:
            return None # Return None if no items found

        # Read the data from the selected item
        with open(os.path.join(self.cachedir, item), 'r') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}

        # Remove the selected item from the cache directory
        tries = 0
        while True:
            try:
                if tries == 5:
                    time.sleep(0.1)
                elif tries >= 10:
                    break # Continue on without removing the file if the file cannot be removed after 10 tries. This prevents an infinite loop.
                os.remove(os.path.join(self.cachedir, item))
                break
            except PermissionError:
                tries += 1
                continue
                # This catches when the error when the file is being written to by another process
                # We do not continue on without removing the file because that would result in the same log being written multiple times
        return data

    def put(self, msg:str, logto, exception:Exception=None, priority=False):
            """
            Writes a log message to a specified log file.

            Args:
                msg (str): The log message to be written.
                logto: The directory where the log file should be written.
                exception (Exception, optional): An optional exception object to be included in the log message. Defaults to None.
                priority (bool, optional): A flag indicating whether the log message has high priority. Defaults to False.
            """
            filename = self.get_filename()

            item = cacheitem_data_table.copy()
            item['directory'] = logto
            item['priority'] = bool(priority)
            item['msg'] = msg
            if exception:
                item['exception'] = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
            else:
                item['exception'] = None

            try:
                with open(filename, 'w+') as f:
                    json.dump(item, f, indent=4, separators=(',', ': '))
            except PermissionError as err:
                return [False, err]

    def get_filename(self):
        os.makedirs(os.path.dirname(self.cachedir), exist_ok=True)
        file = f"qitem_{random.randint(1,99999999999999999999)}.json" # Make sure the file name is unique
        filedir = os.path.join(self.cachedir, file)
        return filedir

    def get_queue_number(self, item):
        item = str(item).replace("qitem_", "").replace(".json", "")
        item = str(item).replace(self.cachedir, "")
        try:
            item = int(item)
        except ValueError:
            raise ValueError(f"Invalid item: {item}")

class pylog:
    def __init__(self, filename='logs/%TIMENOW%.log', logform='%loglevel% - %time% - %file% | '):
        if not filename.endswith('.log'):
            filename += '.log'

        if '%TIMENOW%' in filename:
            filename = filename.replace('%TIMENOW%', datetime.datetime.now().strftime("%Y-%m-%d, %I%p"))

        self.filename = filename
        self.logform = logform

        self.cachedir = global_cachedir
        self.queue = logQueue(self.cachedir)

    def log(self, message):
        '''
        Equivilant to any/all of the logging level functions. Except this one autodetects the logging level.
        '''
        message = str(message)
        message_lower = message.lower()

        for warning_indicator in ['warning', 'warn', 'alert', 'deprecated']:
            if warning_indicator in message_lower:
                self.warning(message)
                return True

        for error_indicator in ['error', 'err', 'exception']:
            if error_indicator in message_lower:
                self.error(message)
                return True
            
        for debug_indicator in ['debug', 'dbg']:
            if debug_indicator in message_lower:
                self.debug(message)
                return True

        self.info(message)
        return True

    def info(self, message):
        logform = self.parse_logform(self.levels.INFO)
        message = f'{logform}{message}'
        self.queue_in({"msg": message, "directory": self.filename})

    def warning(self, message):
        logform = self.parse_logform(self.levels.WARNING)
        message = f'{logform}{message}'
        self.queue_in({"msg": message, "directory": self.filename})

    def error(self, message, exception: Exception):
        logform = self.parse_logform(self.levels.ERROR)
        message = f'{logform}{message}'
        self.queue_in({"msg": message, "directory": self.filename, "exception": exception})

    def debug(self, message):
        logform = self.parse_logform(self.levels.DEBUG)
        message = f'{logform}{message}'
        self.queue_in({"msg": message, "directory": self.filename}, True)

    def queue_in(self, obj, priority=False):
        exception = None
        try:
            exception = obj['exception']
        except KeyError:
            exception = None
        self.queue.put(
            msg=obj['msg'],
            exception=exception,
            priority=priority,
            logto=self.filename
        )

    def parse_logform(self, loglevel):
        logform = self.logform
        logform = logform.replace('%loglevel%', loglevel)
        logform = logform.replace('%time%', datetime.datetime.now().strftime("%Y-%m-%d, %I%p"))
        logform = logform.replace('%file%', f'{inspect.stack()[2][1]}:{inspect.stack()[2][2]}')
        return logform

    class levels:
        DEBUG = "DEBUG"
        INFO = "INFO"
        WARNING = "WARNING"
        ERROR = "ERROR"

def logman():
    cachedir = global_cachedir

    def chunk_searcher(chunk, search_for):
        try:
            if search_for in chunk:
                return True
            else:
                return False
        except KeyboardInterrupt:
            return -1

    def writer():
        queue = logQueue(cachedir)
        if not queue.is_empty(queue_type="priority"):
            log = queue.get(True)
        else:
            log = queue.get()

        if log == None:
            return True

        try:
            os.makedirs(os.path.dirname(log['directory']), exist_ok=True)
            with open(log['directory'], 'a+') as f:
                f.write(log['msg'] + '\n')
        except (PermissionError, OSError) as err:
            err_formatted = traceback.format_exc()
            err_log_msg = f'I encountered an error while logging the following message\n\"{log["msg"]}\"\nMy Error: {err}\n{err_formatted}'
            with open('pylog_error.log', 'r+') as f:
                content = f.read()
            if len(content) < 200_000:
                if err_log_msg not in content:
                    with open('pylog_error.log', 'a+') as f:
                        f.write(err_log_msg)
            else:
                threads = []
                content = content.splitlines()
                for i in range(3):
                    chunk = content[i * 1000: (i + 1) * 1000]
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
                        thread.join()

                    result = thread.exitcode
                    if result == True:
                        break
                    elif result == -1:
                        return True
                else:
                    with open('pylog_error.log', 'a+') as f:
                        f.write(err_log_msg)

    try:
        while True:
            writer()
    except KeyboardInterrupt:
        print("...\nWaiting for logs to be written to file...")
        queue = logQueue(cachedir)
        queue.close()
        queue.close(True)
        while queue.is_empty(queue_type="both") != True:
            writer()
        print("Done writing logs to file.")
