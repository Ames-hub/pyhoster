# File Transfer Protocal (FTP)
### What is FTP?
FTP is a way to transfer files between a client and a server.<br>
It is a very common way to transfer files, and is used by many people.<br>

# How does it relate to PyHoster?
PyHoster has a built-in FTP server that you can use to transfer files to and from your server.<br>
We use a library called pyftpdlib to do this.<br>
It is a very powerful library and I'd like to think we use it well. (btw, I'd recommend them without hesitation for your FTP server needs)<br>

# How do I get started using it?
To use the FTP server, you must first enable it in the settings.<br>
you can do this by using the command "ftp"

Assuming you haven't touched it before,
You will be greeted with a screen that looks like this:
```
FTP server is currently not running.
FTP server is not running but is assigned to port 789.
Use command 'root' to view the root user's connection details.

Anonymous login is currently disabled.
Auto startup is currently disabled.

Welcome to the FTP server CLI. Type "help" for a list of commands.
ftp> 
```
To get started, we need to start the server.<br>
To do this, we use the command "start".<br>
This will start the server on port 789.<br>

We've now got it running, but it won't start automatically when you start the program.<br>
To fix this, we use the command "autoboot" and this will TOGGLE the autoboot setting.<br>
(if its off or on will be indicated in the output)<br>

From here, it's pretty self explanatory.<br>
You can use the command "root" to view the root user's connection details.<br>
That's what you'll use in a client like WinSCP to connect to the server.<br>
##TLDR;
Steps to get started:
1. Enter FTP CLI with "ftp"
2. Start the server with "start"
3. Toggle autoboot on with "autoboot"
4. Use "root" to view the root user's connection details
5. Use a client like WinSCP to connect to the server using the details provided by "root"
6. Your basically done. Just use "add" command to add users to the server.

An example of connecting on WinSCP:
File Protocal: FTP<br>
Encryption: No encryption (I will fix this when I can)<br>
Host name: example_ftp_server.com<br>
Port number: 789<br>
User name: Ame:(app name)<br>
Password: 1234<br>
### Important note
The user name is in the format of "username:(app name)"<br>
This is because the FTP server is designed to allow access to each app specified and this is the only practical way of doing it<br>
The password is global. username must be `username:(app name)`, so eg `amelia:personal web`<br>

# Anonymous Login
Anonymous login is a feature that allows users to login to the server without a username or password.<br>
This is a very useful feature, but it can be dangerous if you're not careful.<br>

To enable anonymous login, use the command "anonlogin".<br>
This will toggle the anonymous login setting.<br>
(If its off or on will be indicated in the output)<br>

# Adding Users
See technical_notes/userman.md for more info on this.<br>
