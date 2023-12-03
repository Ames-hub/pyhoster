# UserMan
This is the user management system for PyHoster.<br>
It allows you to add, remove, and edit users.<br>
NOTE: This feature is still mostly in development.<br>

# Entering
To enter the CLI, simply start the app and type in "userman".<br>
This will bring you to the user management CLI.<br>
From here, a few commands are available to you. They are described in detail below<br>

# Adding Users
To add a user, use the command "add".<br>
This will prompt you for a username and password.<br>
Then it will ask if you want to handle adding directories this user is allowed to access in FTP,<br>
If you pick no, the user will not be able to access FTP.<br>
### Handling FTP
If you pick yes, you will be prompted for an app to allow them to access, then if they can only access its content or not.<br>
This will repeat until you type "done" when prompted for an app.<br>
### End of handling FTP, Now what?
Now it will ask you if you want to use a Preset or Custom FTP permissions.<br>
If you pick preset, you will be prompted for a preset to use.<br>
You can pick either 1 or 2. 2 Is full access<br>
## This is not optional because its essential that permissions are known regardless of if FTP is enabled or not.
If you want to use custom permissions, Read the docs.<br>
https://pyftpdlib.readthedocs.io/en/latest/api.html