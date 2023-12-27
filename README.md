# pyhoster
An nginx replacement built with python to manage multiple website instances easily, efficiently and with control.

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
- File Transfer Protocal with SSL (FTPS) built in and easily configurable with a user system!
- Change the index file of a website easily
- WARDEN, Our basic lockout system allows you to lock out users from a specific webpage (or all webpages) with a password!
- Optionally running API to control what happens in pyhost externally
- Auto-Generate self-signed SSL certificates and put them to use easily! (You can also use your own cert by replacing the file it makes)
- link a website's content to any folder in your system
- Make your changes, then update the website with a simple command
- Built-in function to implement a custom "Page not found" page
- Update messed up your app? No problem! with PyHost you can revert any changes with our full snapshot system!
- Run multiple websites at once
- User friendly design

# The PyHost API
PyHost has an API that you can use to control what happens in pyhost externally.<br>
Using the API, you can do things such as start and stop websites, create and delete websites, etc.<br>
For full details, see the technical_notes/API.md file.
### We also have a session manager!
It'll kill old sessions, start new ones and let you kill specific sessions!

# Compatibility
This works on every OS as far as I know.<br>
As long as the OS can run one of the listed compatible versions of python, it should be able to run this.<br>
There's nothing stopping it from doing so at least<br>

Only exception is MacOS/OSX. I don't have a mac to test it on and I'm assuming Mac uses different OS commands and directories.<br>
(However, just because its not tested on mac doesn't mean it won't work. Try it and lmk, worst you'll get is an error message.)

So far I've tested it on<br>
ZorinOS (ubuntu based)<br>
Ubuntu<br>
Windows 11 (Developed on.)

Tested/Compatible Python Versions:
- 3.12 (Assumed compatible)
- 3.11 (Compatible, Tested & Developed on)
- 3.10 (Compatible)

# Why do we exist?
I've faced challenges with mainstream web hosting services like Nginx and Apache. Nginx wasn't straightforward; even after following its instructions, I encountered SSL errors before considering SSL itself. Apache initially worked, but it mysteriously stopped functioning after a couple of days without any error messages. Frustrated, I decided to create my own solution—pyhoster. It's a Python-based website manager with a simple interface, requiring only a few commands for setup. No extensive configuration needed; it's meant to be a hassle-free hosting option.

## Possible Commands
`webcreate` - Create a new website app.<br>
`wsgicreate` - Create a new wsgi app. (WIP)<br>
`delete` - Delete an app.<br>
`edit` - Edit a website app.<br>
`start` - Start a website app.<br>
`stop` - Stop a website app<br>
`restart` - Stop and then start a website app. Shorthand way of doing stop app_name && start app_name<br>
`idle` - Go into an IDLE screen to display information while pyhost does its thing in the background!<br>
`pyhost` - Access the settings of pyhoster.<br>
`exit` - Exit the program.<br>
`domain` - Set the domain name/IP Address used by PyHost for the WebGUI and any other features<br>
`update` - Updates the content of a website app.<br>
`rollback` - Reverts the content of a website app to the last update, or a specific version.<br>
`enter (feature)` - Enter the Command Line Interface (CLI) for a feature such as FTP, UserMan or Warden.<br>
`ftp` - Enter the FTP Command line interface. Change details, create users, etc<br>
`userman` - Enter the UserMan Command line interface. Change details, create users, etc<br>
`userman > sessions` - Enter the Session Manager CLI within the Userman CLI.<br>
`warden` - Enter the Warden Command line interface. Change details, create users, etc<br>
`cls` - Clear the screen of all text.<br>
`ctrl + c` (signal 2) - Exit the program and shutdown all web apps.<br>

# Technical and Configuration Details
### Environment variables
PYHOST_COMMANDS_LISTEN: Boolean (True, False), if true, pyhoster will start an input line. (Default: True)
made toggleable for 'edge' cases where you want to use the keybinds for something else.

### Default pages
PyHoster has a few default pages that you can use for your website.<br>
- 404 Page - The index is found but the requested page is not found. (Default: 404.html. User created, default.html is blank)
- Index not found - The page shown when the index file is not found. (Default: default.html)
- Index - The index file of the website. Can be custom set. (Default: index.html)

### Security configuration
PyHoster has a few optional security features built in.<br>
- SSL - PyHoster can generate a self-signed SSL certificate for your website or use your own. (Default: True)
- File directory Listing toggle. - Toggle whether or not to allow directory listing. (Default: False)
- Security Headers toggler - PyHoster can add security headers to your website. (Default: True)
- CSP Directives - add CSP directives to your website! (Default: True)
- Webpage locking - Lock out users from a webpage with a password. (See bottom of technical_notes/warden.md)
