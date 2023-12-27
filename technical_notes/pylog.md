# pylog.py Documentation

This Python script provides a logging system that writes log messages to a file. It uses a priority queue system to manage the logs and writes them to a file asynchronously.

## Import Statements

The script begins by importing necessary modules:

- `multiprocessing`: This module allows for the creation of separate processes, which can run concurrently. This is used in the `logman` function to search for a specific string in chunks of text.
- `traceback`: This module is used for handling and formatting exceptions. It's used in the `logQueue` and `pylog` classes to format exceptions that occur during logging.
- `datetime`: This module is used to get the current date and time, which is used in the filename of the log file and in the log messages themselves.
- `inspect`: This module is used to retrieve information about the current execution context. It's used in the `parse_logform` method of the `pylog` class to get the file name and line number where the log message was generated.
- `json`: This module is used for reading and writing JSON files. It's used in the `logQueue` class to store and retrieve log messages in JSON format.
- `os`: This module is used for interacting with the operating system, such as creating directories and listing files in a directory.

## Global Variables

The script defines a global variable `global_cachedir` which is the directory where the log files will be cached. This directory is used by the `logQueue` class to store and retrieve log messages.

## logQueue Class

This class manages the queue of log messages. It has several methods:

- `__init__`: Initializes the log queue with a specified cache directory.
- `is_empty`: Checks if a directory is empty based on the specified queue type ('priority' or 'normal'). This is used to determine if there are any log messages of a certain priority that need to be written to the file.
- `close` and `open`: These methods close and open the queue for a specific priority. This is used in the `logman` function to stop adding new log messages to the queue when a keyboard interrupt is received.
- `get`: Retrieves data from the cache directory. If the `priority` argument is `True`, it retrieves data with priority; otherwise, it retrieves non-priority data.
- `put`: Writes a log message to a specified log file. The `priority` argument determines whether the log message has high priority.
- `get_filename`: Generates a filename for a new log file in the cache directory.
- `get_queue_number`: Retrieves the queue number for a given item. This is used to determine the order in which log messages are written to the file.

## pylog Class

This class manages the logging system. It has several methods:

- `__init__`: Initializes the logger with a specified filename and log format.
- `info`, `warning`, `error`, `debug`: These methods log a message with the corresponding log level. The `error` method also takes an exception as an argument, which is included in the log message.
- `queue_in`: Puts a log message into the queue. The `priority` argument determines whether the log message has high priority.
- `parse_logform`: Parses the log format string and replaces placeholders with actual values. The placeholders include the log level, the current time, and the file name and line number where the log message was generated.

## logman Function

This function manages the writing of log messages from the queue to the file. It has two inner functions:

- `chunk_searcher`: Searches for a specific string in a chunk of text. This is used to avoid writing duplicate error messages to the `pylog_error.log` file.
- `writer`: Writes log messages from the queue to the file. It first checks if there are any priority log messages in the queue, and if so, writes them to the file. Otherwise, it writes non-priority log messages to the file.

The `logman` function runs an infinite loop that continuously calls the `writer` function to write log messages to the file. The loop can be interrupted with a keyboard interrupt, after which it will finish writing all remaining log messages to the file before terminating.

# PRACTICAL USE
## Logging with `pylog.py`

This document explains the process of creating a new log using the `pylog.py` module.

## Step 1: Import the `pylog` class

First, you need to import the `pylog` class from the `pylog.py` module.

```python
from pylog import pylog
```

## Step 2: Create an instance of `pylog`

Next, create an instance of the `pylog` class. You can specify the filename and log format as arguments. If not provided, the default values will be used.

```python
logger = pylog(filename='my_log.log', logform='%loglevel% - %time% - %file% | ')
```

## Step 3: Log a message

You can log a message using one of the following methods: `info`, `warning`, `error`, or `debug`. The message will be queued in the log file.

```python
logger.info("This is an informational message.")
logger.warning("This is a warning message.")
logger.error("This is an error message.")
logger.debug("This is a debug message.")
```

If you're logging an error, you can also include an exception object as an argument:
We don't just find the latest exception because another exception may have happened before we get to the error.
```python
try:
    1/0
except Exception as e:
    logger.error("An error occurred.", e)
```

## Step 4: Write the logs to file

The `logman` function is responsible for writing the logs to the file. It checks the queue for any logs and writes them to the file. If there's an error while writing the logs, it logs the error in a separate file named `pylog_error.log`.<br>
logman is a blocking function, so it must be ran in a thread using either multiprocessing or threading.<br>
(A blocking function: Code, in this case a function, which prevents more code from being ran until it is completed or terminated.)

```python
from pylog import logman
import multiprocessing as mp

if __name__ == "__main__": 
    logman = mp.Process(target=logman, args=())
    logman.start()
```

This function runs in an infinite loop, so it will keep checking for new logs and write them to the file until the program is interrupted.

## Note

The `pylog` class uses a priority queue for logging. If a log message is marked as a priority (like debug logs), it will be written to the file before other log messages.

# Caching in `pylog.py`

The `pylog.py` script uses a caching mechanism to handle logging operations. This mechanism is implemented through the `logQueue` class, which manages a cache directory where log messages are temporarily stored before being written to their respective log files.

## How Does the Caching Work?

The `logQueue` class manages the cache directory. Each log message is stored in a separate JSON file in the cache directory. The JSON file contains the log message, its priority, and the directory where it should be written.

The `logQueue` class provides several methods for interacting with the cache:

- `is_empty(queue_type)`: Checks if the cache is empty for a specific queue type ('priority' or 'normal').

- `close(priority)`: Closes the cache for a specific queue type.

- `open(priority)`: Opens the cache for a specific queue type.

- `get(priority)`: Retrieves a log message from the cache. If the 'priority' argument is True, it retrieves a log message with a high priority.

- `put(msg, logto, exception, priority)`: Adds a log message to the cache.

## Conclusion
This script provides a robust logging system that can handle a large number of log messages and write them to a file asynchronously. It uses a priority queue system to manage the logs, ensuring that high-priority logs are written to the file first.<br>
(AI Generated documentation, Thank you OpenAI)