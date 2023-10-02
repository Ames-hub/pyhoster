from .jmod import jmod
from .data_tables import config_dt

class autostart:
    def add(app_name):
        config = config_dt(app_name)
        jmod.setvalue(
            key=f"{app_name}.autostart",
            json_dir=f"instances/{app_name}/config.json",
            value=True,
            dt=config
        )

    def remove(app_name):
        config = config_dt(app_name)
        jmod.setvalue(
            key=f"{app_name}.autostart",
            json_dir=f"instances/{app_name}/config.json",
            value=False,
            dt=config
        )