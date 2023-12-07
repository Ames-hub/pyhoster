# API: Application Programming Interface
## What is an API?
An API is a set of functions to interact with a program. It is a way to interact with a program without having to know how it works. For example, when you use a library in Python, you don't need to know how the library works, you just need to know how to use it. The library is the API.

## Pyhost API
Pyhost has an API to interact with the application. This includes Starting instances, stopping instances, etc.
Pyhost uses FLASK

Default port: 987

# Permissions
On pyhost, we have a permissions system to control how a user is allowed to interact with the API.
There are 2 presets by default. Admin and User. Admin has full access to the API, while user can only start and stop instances.

## Permissions logic
The permissions system is based on a substring permission indication system. Eg:
Someone with the permission string "sS" can start and stop instances, but not create or delete them.

### Index
| Permission | Description |
| ---------- | ----------- |
| s | Start instances
| S | Stop instances
| c | Create instances
| d | Delete instances

-- WARDEN PERMISSIONS --
| -WP- | Modify warden pin
| -WA- | Toggle warden On/Off
| -WPA- | Add a page to warden
| -WPD- | Delete a page from warden

-- FTP PERMISSIONS --
| -FAB- | Toggle FTP Autoboot On/Off
| -FA- | Turn off/on FTP Server
| -FL- | View FTP Logs

-- ADMIN PERMISSIONS --
| -UL- | Lock/Unlock a user account
| -UP- | Change a user's password
| -UD- | Delete a user account
| -UC- | Create a user account
| -U- | View user accounts
| -PYHOST_SHUTDOWN- | Perform a shutdown command on the application