import os,multiprocessing as threading
try:
    from .jmod import jmod
    from .data_tables import web_config_dt, wsgi_config_dt
    from .pylog import pylog
except ImportError as err:
    print("Hello! To run Pyhost, you must run the file pyhost.py located in this projects root directory, not this file.\nThank you!")
    from library.pylog import pylog
    pylog().error(f"Import error in {__name__}", err)
root_dir = os.getcwd()
pylogger = pylog()

class autostart:
    def add(app_name, start_app=True):

        port_taken = False
        # Checks all other projects for other autostarts that have the same port
        for app in os.listdir("instances/"):
            config_file = f"instances/{app}/config.json"
            if jmod.getvalue(key=f"autostart", json_dir=config_file) == True:
                port = jmod.getvalue(key='port', json_dir=config_file)
                if port == jmod.getvalue(key='port', json_dir=f"instances/{app_name}/config.json"):
                    pylogger.info(f"Port {port} is already in use by project {app}! Please change the port of one of the projects to add to autostart.")
                    port_taken = True

        jmod.setvalue(
            key="autostart",
            json_dir=f"instances/{app_name}/config.json",
            value=True,
            dt=web_config_dt
        )

        if start_app is True:
            from .instance import instance
            website = threading.Process(
                target=instance.start, args=(app_name, False),
                name=f"{app_name}_webserver"
                )
            website.start()
            pid = website.pid
            jmod.setvalue(
                key="pid",
                json_dir=f"instances/{app_name}/config.json",
                value=pid,
                dt=web_config_dt
            )
            del instance # Free up memory (Idk if it already does this)
        
        return True if not port_taken else False

    def remove(app_name):
        jmod.setvalue(
            key="autostart",
            json_dir=f"instances/{app_name}/config.json",
            value=False,
            dt=web_config_dt
        )