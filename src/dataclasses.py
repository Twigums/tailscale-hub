from dataclasses import dataclass, field
from typing import Dict, List

# init config
@dataclass
class AppConfig:
    main_color: str = ""
    secondary_color: str = ""

    additional_ports: Dict = field(default_factory = dict)
    http_ports: List[int] = field(default_factory = list)
    https_ports: List[int] = field(default_factory = list)

    # check if user is using mobile or not
    is_mobile: bool = False

    ui_port: int = 8080
    ui_web_title: str = "twilscale hub"
    ui_storage_secret: str = "test"
    debug_mode: bool = False