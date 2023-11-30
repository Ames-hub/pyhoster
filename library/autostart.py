import os,multiprocessing as threading
from .jmod import jmod
from .data_tables import web_config_dt, wsgi_config_dt
root_dir = os.getcwd()
class autostart:
    def add(app_name, start_app=True):

        port_taken = False
        # Checks all other projects for other autostarts that have the same port
        for app in os.listdir("instances/"):
            config_file = f"instances/{app}/config.json"
            if jmod.getvalue(key=f"autostart", json_dir=config_file) == True:
                port = jmod.getvalue(key='port', json_dir=config_file)
                if port == jmod.getvalue(key='port', json_dir=f"instances/{app_name}/config.json"):
                    print(f"Port {port} is already in use by project {app}! Please change the port of one of the projects to add to autostart.")
                    port_taken = True

        jmod.setvalue(
            key="autostart",
            json_dir=f"instances/{app_name}/config.json",
            value=True if not port_taken else False, # If the port is taken, it will not add it to autostart
            dt=web_config_dt
        )

        if start_app is True:
            from .instance import instance
            website = threading.Process(
                target=instance.start, args=(app, False),
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