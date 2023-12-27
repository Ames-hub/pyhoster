# Instances/Apps
The most fundamental feature of PyHost.<br>
There is lots to apps, but here I will just write down what comes to mind and what is important.<br>

Directory:<br>
./instances/{APP_NAME}<br>
Content Directory:<br>
./instances/{APP_NAME}/content/

# Backups
By default, apps are backed up on every detected change when comapred to a previous backup.<br>
See ./technical_notes/snapshot_system.md for more information.

# Data required for creation
1. *App Name
2. *App Port
3. *Do Autoboot
4. App Description
5. Bound Path (Defaults to content directory)

# Deleting an app
Deleting an app is simple. You delete the directory and pyhost will only have its backups.<br>
Using the built-in method however can remove those backups too.<br>
Where those backups are stored, should be mentioned in ./technical_notes/snapshot_system.md

# Types of Apps
## Webapp
WebApps are what PyHost was built for. it can run these best, and they are more tested than WSGI apps.
## WSGIApp
WSGI apps are something that was added on as a "good idea".<br>
The idea has not been focused on much, and to this day (24/12/2023) full implementation has not been approached.<br>
TODO: Fully implement WSGI apps
### What WSGI apps use
WSGI apps use Waitress. a Python WSGI library.
