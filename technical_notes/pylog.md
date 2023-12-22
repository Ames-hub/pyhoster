# Custom Logging Function

### Overview
This script defines a custom logging utility named `pylog` for writing log messages to a file. It is designed to handle multi-threaded applications or scenarios with multiple files that need to log to the same file.

## Getting Started
1. Import the `logman` function from the `pylog` file and run it in a separate thread. This step is crucial for log messages to be written to the file.
2. Import the `pylog` class from the `pylog` file.
3. Create a `pylog` object, specifying the log file name and format.
4. Create a `LogMan` thread and run it.
5. Start logging using the created `pylog` object.

### `pylog` Class
#### Initialization
- `filename` (str): The name of the log file. Defaults to 'logs/%TIMENOW%.log'.
- `logform` (str): The log message format. Defaults to '%loglevel% - %time% - %files | '.
- `uselatest` (bool): Whether to create a 'latest.log' file before renaming on the next session. Defaults to True.

#### Attributes
- `filename` (str): The name of the log file.
- `logform` (str): The log message format.

### Log Levels
- DEBUG
- INFO
- WARNING
- ERROR

### Methods
0. `debug(message: str)`: Logs a debug message. Log msg's used with this method are moved to the top of the queue
1. `info(message: str)`: Logs an informational message.
2. `warning(message: str)`: Logs a warning message.
3. `error(message: str, exception: Exception)`: Logs an error message along with exception details.

### Internal Methods
1. `queue_in(message: str)`: Adds a message to the log queue.
2. `parse_logform(loglevel: str) -> str`: Parses the log message format, replacing placeholders with actual values.

### `logman` Function
- This function is a worker that writes logs to a file from the queue.
- Should be run only once and ensure it runs only once to prevent log overwrites.
- Handles scenarios with multiple threads/files running this function.

### `writer` Function (Internal to `logman`)
- Writes logs to the file from the queue.
- Manages the creation and renaming of log files based on settings.
- Handles errors and logs them appropriately.

### Consequences to > 1 logman instances running
If Logman is running more than once, it will result in Log files being
1. Overwritten (potentially)
2. Data being left out
3. Exceptions
It should never be allowed to happen.
Logman exists and is only ran ONCE to prevent an old bug where if multiple files
tried to write to the same log file, They'd overwrite eachother and there'd be conflicts.
The queue system paired with logman allows for there to be no conflicts.

### Priority Queue
A Priority queue exists and mainly exists for `pylog.debug`
If normal queue has 100 in it but priority has 1 in it, it'll do priority first.
Same for the reverse

### Usage Example
```python
from pylog import logman
import multiprocessing

# Create and start the LogMan thread
if __name__ == "__main__": # Only start once. Never start a second logman.
    logman_thread = multiprocessing.Process(target=logman, args=())
    logman_thread.start()

# Create a pylog object
logger = pylog(
    filename='logs/application.log',
    logform='%loglevel% - %(time)s | '
)

# Start logging
logger.info('Hello World!')
```

Note: Ensure the `logman` thread is running for log messages to be written to the file.