# Pyhost WebGUI
A WebGUI (Website Graphgical User Interface) for pyhost which allows users to easily interact with Pyhost without using a CLI (Command Line Interface)

Default port: 4040<br>
Content in: library/WebGUI/content/

Controlled using webgui.py which is imported by application.py and used in application.run()

It is controlled mostly Like a normal webinstance. Only exception is that its more restricted from easy modification (aside from the websites look, which is modifiable via content directory)

to interact, start pyhost and use command "webgui"

Minimum supported resolution: 800x611 (for the webgui to look good, no squashing, etc.)