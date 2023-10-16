# pyhoster
An nginx replacement built with python to manage multiple website instances.

## Installation
Install python3.12 from the website or your package manager. (Such as MS store)
then run these commands in the directory you want to install pyhoster in.
```
git clone https://github.com/Ames-hub/pyhoster . 
python3.12 -m venv venv
```
wait for the venv to install (may take a minute)

on windows, use `venv\Scripts\activate.bat` to activate the virtual environment.<br>
on linux, use `source venv/bin/activate` to activate the virtual environment.

then run `pip install -r requirements.txt` to install what is needed.

Then run `python3.12 pyhost.py -O` to start the program.

# Features
- Create and delete website's in a second (simple as `create websitename`)
- Start and stop websites easily (simple as `stop websitename`)
- Edit the settings and content of a website easily
- Change the index file of a website easily
- link a website's content to any folder in your system
- Make your changes, then update the website with a simple command
- Built-in function to implement a custom "Page not found" page
- Update messed up your app? No problem! with PyHost you can revert any changes with our full snapshot system!
- Run multiple websites at once
- User friendly design

# Compatibility
This works on every OS as far as I know.<br>
As long as the OS can run python3.11 or 3.12, it should be able to run this.<br>
There's nothing stopping it from doing so at least<br>

So far I've tested it on<br>
ZorinOS (ubuntu based)<br>
Ubuntu<br>
Windows 11

Tested Python Versions:
- 3.10
- 3.11
- 3.12

# Environment variables
PYHOST_KEYBIND_LISTEN: Boolean, if true, pyhoster will listen for keybinds. (Default: True)
made toggleable for 'edge' cases where you want to use the keybinds for something else.

# Possible Commands
if a key is in brackets, I am indicating its on the keyboard and not to be typed out<br>
`create` - Create a new website app.<br>
`delete` - Delete a website app.<br>
`edit` - Edit a website app.<br>
`start` - Start a website app.<br>
`stop` - Stop a website app<br>
`restart` - Stop and then start a website app. Shorthand way of doing stop app_name && start app_name<br>
`update` - Updates the content of a website app.<br>
`rollback` - Reverts the content of a website app to the last update, or a specific version.<br>
`cls` - Clear the screen of all text.<br>
`ctrl + c` - Exit the program and shutdown all web apps.<br>
