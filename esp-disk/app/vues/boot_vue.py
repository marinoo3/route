from app.vues.base import Vue
from app.vues.elements import DisplayElement, Console

import time

TYPE_CHECKING = False
if TYPE_CHECKING:
    from app.modules import Display


class BootVue(Vue):
        
    def _logic_loop(self) -> None:
        return super()._logic_loop()

    # ------- EVENT HANDLER

    def _handle_wifi_fail(self, display: "Display") -> None:
        """
        Display retry dialog and wait for user to click
        """
        display.set_value(
            "log",
            value={
                'message': "Connection",
                'console': ["Failed!"],
                'action': "Retry"
            }
        )
    
    # ------- VUE LOADING

    def load(self, display: "Display") -> None:
        display.add_element(
            "log",
            Console(
                "log",
                0, 0, 128, 32
            )
        )

        self.bind(
            "wifiConnection",
            lambda ssid: display.set_value(
                "log",
                value={
                    'message': "Connection",
                    'console': ["Network:", ssid]
                }
            )
        )
        self.bind(
            "wifiFailed",
            lambda: self._handle_wifi_fail(display)
        )
        self.bind(
            "calibrateGyro", 
            lambda bias: display.set_value(
                "log", 
                value={
                    'message': "Calibration",
                    "console": [f"Bias: {round(sum(bias), 3)}"]
                }
            )
        )
        self.bind(
            "createSession", 
            lambda: display.set_value(
                "log", 
                value={'message': "Loging"}
            )
        )
        self.bind(
            "done", 
            lambda: display.set_value(
                "log", 
                value={'message': "Done"}
            )
        )