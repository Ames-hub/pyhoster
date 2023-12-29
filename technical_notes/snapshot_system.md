# Technical Notes for `snapshots.py` in Pyhost

## Import Statements

- The code imports several modules such as `os`, `shutil`, `hashlib`, `time`, and `sys`.
- Custom modules like `jmod`, `pylog`, and `data_tables` are imported, containing utility functions for the Pyhost project.

## Constants

- Several constants are defined for better code readability, including color codes for console output (`orange`, `cyan`, `green`, `white`, `gray`), and a time duration constant (`four_hours`).

## Class: snapshots

### Function: `update`

- Updates an app by copying files from an external directory to an internal directory.
- Takes a snapshot of the current app directory before updating.
- Removes old files and directories from the app directory.
- Duplicates files from the external directory to the app directory.

### Function: `clear_content`

- Clears the content of a directory to prepare for an update.
- Removes files and directories, handling permission errors.
- Returns a tuple indicating the success of the operation and the number of files processed.

### Function: `check_outdated`

- Checks if an app is outdated by comparing file hashes between internal and external directories.
- Returns a boolean indicating whether the app is outdated and handles cases where external files are missing.

### Function: `get_backup_dir`

- Gets the directory to backup the app instance to.
- Considers user preferences and platform-specific default paths.
- Creates the backup directory if it doesn't exist.

### Function: `get_rollback_app`

- Retrieves the name of an app from the user.
- Different variants for rollback, backup, or update, depending on the provided integer variant.
- Presents a list of apps with highlighting based on their update time.

### Function: `rollback`

- Rolls back the specified app to a previous version.
- Stops the app, overwrites it with the backup, and starts the app again.
- Handles version selection, backup directory creation, and potential errors during the rollback process.

### Function: `backup`

- Creates a backup snapshot of the specified app instance.
- Copies the app directory to a backup directory.
- Considers user preferences for backup location and handles potential errors during the backup process.

AI Generated Docs. Thank you ChatGPT