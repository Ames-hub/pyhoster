# Pyhost WebGUI
A WebGUI (Website Graphgical User Interface) for pyhost which allows users to easily interact with Pyhost without using a CLI (Command Line Interface)

# IMPORTANT NOTICE
The WebGUI has 2 modes. One of which, I cannot test. But can only assume that it works in theory. They are described below.
This has come after a long time of learning CORS and trying to figure out why the WebGUI cannot access the API when running on HTTPS
## Mode 1. "Closed Mode" (TESTED)
In this mode, Only LocalHost can access the WebGUI and all other requests may make it to the Login screen, but it'll stop there.<br>
The reason for this is they'll encounter CORS (Cross Origin Resource Sharing) errors upon further attempts. In the future, we have it to, depending on the mode,
Simply return a 403 Error.
This also means that in this mode, it wont use HTTPS and will instead use HTTP. Which is fine considering in this mode, it wouldn't be port-forwarded to be readable.<br>
This shouldn't be too much of a problem, as Pyhost is meant to be ran on a server where Mode 2 would be used and not your local machine.
## Mode 2. "Remote Mode" (As of now, Not possible to test until further research is done.)
In this mode, It will be running in HTTPS and running accessible on the Domain you provide on the set port for any member with knowledge of a set of login details, but inaccessable on LocalHost. (But most likely still accessible if you go to the domain, as a name and not an IP, ON the localhost?)<br><br>

In summary, Remote Mode lets other people access your WebGUI assuming they have a PyHost Logon assigned to them.

### Important variables
Default port: 4040<br>
Content in: library/WebGUI/content/

# Description
It is controlled mostly Like a normal webinstance. Only exception is that its more restricted from easy modification (aside from the websites look, which is modifiable via content directory)

to interact, start pyhost and use command "webgui"

## Things to consider 
Minimum supported resolution: 800x611 (for the webgui to look good, no squashing, etc.)