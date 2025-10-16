import tomllib

from nicegui import ui, app

from src.nicegui.main_tab import MainTab
from src.nicegui.options_tab import OptionsTab
from src.dataclasses import AppConfig


def check_device(config: AppConfig) -> None:
    res = ui.context.client.request.headers["user-agent"]

    config.is_mobile = "Mobile" in res
    print(f"Connected from: {res}")

    return None

def setup_styles() -> None:

    # css
    ui.add_head_html("""
        <style>
            .main-text {
                font-family: 'Noto Sans', sans-serif;
                font-size: 2rem;
            }
        </style>
    """)

    return None

# very important -> dark mode
def setup_dark_mode() -> None:
    if "is_dark_mode" not in app.storage.user:
        app.storage.user["is_dark_mode"] = False

    ui_dark = ui.dark_mode()
    ui_dark.value = app.storage.user["is_dark_mode"]

    return None

def create_page(config: AppConfig) -> None:

    # setup
    setup_styles()
    setup_dark_mode()

    # main items on the website
    header = ui.header().style(f"background-color: {config.main_color}; color: white;")
    tabs = ui.tabs().classes("w-full")

    with header:
        ui.label(config.ui_web_title).classes("text-h4 q-px-md")

    # define our tabs we will use
    with tabs:
        main_tab = ui.tab("Main")
        options_tab = ui.tab("Options")

    # main tab should be the default
    with ui.tab_panels(tabs, value = main_tab).classes("w-full"):

        # we should show stats and refresh it automatically!
        with ui.tab_panel(main_tab):
            MainTab(config)

        # options tab
        with ui.tab_panel(options_tab):
            OptionsTab()

    return None

def main():
    with open("config.toml", "rb") as f:
        config = tomllib.load(f)

    config_app = AppConfig(
        main_color = config["main_color"],
        secondary_color = config["secondary_color"],
        additional_ports = config["ports"],
        http_ports = config["http"]["ports"],
        https_ports = config["https"]["ports"]
    )

    app.on_connect(lambda: check_device(config_app))

    @ui.page("/")
    def index() -> None:
        create_page(config_app)

    # for the sake of testing, be able to change port to whatever
    import sys

    if len(sys.argv) == 2:
        config_app.ui_port = int(sys.argv[1])

    # serve site
    ui.run(port = config_app.ui_port,
           title = config_app.ui_web_title,
           storage_secret = config_app.ui_storage_secret
    )

# start serving the site
if __name__ in {"__main__", "__mp_main__"}:
    main()