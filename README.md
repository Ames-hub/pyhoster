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
- File Transfer Protocal with SSL (FTPS) built in and easily configurable and usable!
- Our lock-out system 'Warden' allows you to lock out users from a specific webpage or website with a password!
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

Only exception is MacOS/OSX. I don't have a mac to test it on, but quite frankly you shouldn't be using a mac to host a website anyway.<br>
(However, just because its not tested on mac doesn't mean it won't work. Try it and lmk, worst you'll get is an error message.)

So far I've tested it on<br>
ZorinOS (ubuntu based)<br>
Ubuntu<br>
Windows 11

Tested Python Versions:
- 3.10
- 3.11
- 3.12

# Why do we exist?
I've been asked this question somewhat often, so I decided to make a section for it.<br>
When I was first trying to finally host my website that I had made, I was looking for a good service to do it.<br>
I immediately went to the obvious ones, Nginx and Apache. I tried both, and they Both had their own problems.<br>

Nginx, when I first started using it, Was not something that just Worked. You couldn't set a couple variables such as<br>
"You can find my website's content and index file here, now do it." and when I did what it wanted, I got an SSL error<br>
BEFORE I even considered using SSL! And it never ended up working properly. (until 1 time where it just works for no apparent reason)<br>

I tried apache, messed around with it, got it working. but then 2 days later it stopped working and I couldn't figure out why.<br>
I didn't even get an error message from the docker container!

So I decided to make my own. I wanted something that was easy to use with atleast a basic UI<br>
something easy to configure, and easy to manage but most importantly, something that just worked out of the box.<br>

So I made pyhoster, A Python website manager where you merely have to type in a few hand-held commands and you're done.<br>
Additional configuration entirely optional.

## Possible Commands
`webcreate` - Create a new website app.<br>
`wsgicreate` - Create a new wsgi app.<br>
`delete` - Delete a website app.<br>
`edit` - Edit a website app.<br>
`start` - Start a website app.<br>
`stop` - Stop a website app<br>
`restart` - Stop and then start a website app. Shorthand way of doing stop app_name && start app_name<br>
`update` - Updates the content of a website app.<br>
`rollback` - Reverts the content of a website app to the last update, or a specific version.<br>
`cls` - Clear the screen of all text.<br>
`ctrl + c` (signal 2) - Exit the program and shutdown all web apps.<br>

# Technical and Configuration Details
### Environment variables
PYHOST_KEYBIND_LISTEN: Boolean (True, False), if true, pyhoster will listen for keybinds. (Default: True)
made toggleable for 'edge' cases where you want to use the keybinds for something else.

### Default pages
PyHoster has a few default pages that you can use for your website.<br>
- 404 Page - The index is found but the requested page is not found. (Default: 404.html. User created, default.html is blank)
- Index not found - The page shown when the index file is not found. (Default: default.html)
- Index - The index file of the website. Can be custom set. (Default: index.html)

### Security configuration
PyHoster has a few optional security features built in.<br>
- SSL - PyHoster can generate a self-signed SSL certificate for your website or use your own. (Default: False)
- File directory Listing toggle. - Toggle whether or not to allow directory listing. (Default: False)
- Security Headers toggler - PyHoster can add security headers to your website. (Default: True)
- CSP Directives - add CSP directives to your website! (Default: True)
- Webpage locking - Lock out users from a webpage with a password.
