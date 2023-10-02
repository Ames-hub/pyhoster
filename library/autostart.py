from .jmod import jmod
from .data_tables import config_dt

class autostart:
    def add(app_name):
        jmod.setvalue(
            key=f"{app_name}.autostart",
            json_dir=f"instances/{app_name}/config.json",
            value=True,
            dt=config_dt(app_name)
        )

    def remove(app_name):
        jmod.setvalue(
            key=f"{app_name}.autostart",
            json_dir=f"instances/{app_name}/config.json",
            value=False,
            dt=config_dt(app_name)
        )