from nicegui import app, ui
from nicegui.events import ValueChangeEventArguments

class OptionsTab(ui.element):
    def __init__(self):
        super().__init__()

        # set up how the dark mode button looks
        self.dark = ui.dark_mode()
        self.dark.value = app.storage.user["is_dark_mode"]
        self.dark_switch = ui.switch("Dark Mode", on_change = lambda e: self.save_dark_mode(e)).bind_value(self.dark)

        ui.separator()

        ui.button("Reload page", on_click = ui.navigate.reload)

    # also refresh when switched because there's a weird bug with other tabs not being in dark mode
    def save_dark_mode(self, e: ValueChangeEventArguments) -> None:
        if app.storage.user.get("is_dark_mode", False) != e.value:
            app.storage.user["is_dark_mode"] = e.value
            ui.navigate.reload()

        return None