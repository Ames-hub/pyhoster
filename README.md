# pyhoster
An nginx replacement built with python to manage multiple website instances.
No longer a replacement, but a wrapper for nginx. God Nginx made me want to cry at first which is what started this project.

## Installation
Install python3.11 from the website or your package manager. (Such as MS store)
then run these commands in the directory you want to install pyhoster in.
```
git clone https://github.com/Ames-hub/pyhoster .
python3.11 -m venv venv
```
on windows, use `venv\Scripts\activate.bat` to activate the virtual environment.<br>
on linux, use `source venv/bin/activate` to activate the virtual environment.

then run `pip install -r requirements.txt` to install what is needed.

Then run `python3.11 pyhost.py -O` to start the program.

# Environment variables
PYHOST_KEYBIND_LISTEN: Boolean, if true, pyhoster will listen for keybinds. (Default: True)
made toggleable for 'edge' cases where you want to use the keybinds for something else.

# Keybinds/Keywords
if a key is in brackets, I am indicating its on the keyboard and not to be typed out<br>
`create + [enter]` - Create a new website instance.<br>
`delete + [enter]` - Delete a website instance.<br>
`cls + [enter]` - Clear the screen of all text.<br>
`ctrl + c` - Exit the program and shutdown all web instances.<br>

<hr>
In the future, I plan to make this independant from Nginx so that it can run without docker or nginx.