from app.scripts import connect_wifi
from app.models import IMUSamplesBuffer
from app.models.event import Event
from app.modules import IMUSensor
from app.services import API, Ui
from app.vues import BootVue, RecordVue

import time
import uasyncio as asyncio


class Controller:

    def __init__(
            self,
            imu: IMUSensor,
            ui: Ui,
            api: API,
            push_frecency_sec: int,
            ssid: str,
            pwd: str
        ) -> None:
        self.imu = imu
        self.ui = ui
        self.api = api
        self.push_frecency_ms = push_frecency_sec * 1000
        self.buffer = IMUSamplesBuffer()
        self.wifi_credientials = {
            'ssid': ssid,
            'pwd': pwd
        }

        # Start UI loop
        asyncio.create_task(self.ui.run())
        self._last_click = self.ui.button.last_click 

        # Start IMU loop
        asyncio.create_task(self.imu.run())

    def _now(self) -> int:
        """
        Get current time in micro seconds

        Returns:
            int: Current time
        """
        return time.ticks_ms()
    
    def _check_click(self) -> bool:
        """
        Check if new button has been clicked since last check

        Returns:
            bool: Has button been clicked
        """
        button_click = self.ui.button.last_click

        if button_click != self._last_click:
            self._last_click = button_click
            return True
        
        return False
    
    async def run(self) -> None:
        """
        Init boot sequence then load record vue
        """
        await self.boot()
    
    async def boot(self) -> None:
        """
        Start boot sequence
        """
        self.ui.load_vue(
            BootVue()
        )

        self.ui.dispatch_event(Event("wifiConnection", ssid=self.wifi_credientials['ssid']))
        self.ui.update()
        while not await connect_wifi(*self.wifi_credientials.values()):
            self.ui.dispatch_event(Event("wifiFailed"))
            while not self._check_click():
                await asyncio.sleep(0.0005)

            self.ui.dispatch_event(Event("wifiConnection", ssid=self.wifi_credientials['ssid']))        

        for bias in self.imu.calibrate_gyro_bias():
            self.ui.dispatch_event(Event("calibrateGyro", bias=bias))
            self.ui.update()
            await asyncio.sleep(0.005)

        self.ui.dispatch_event(Event("createSession"))
        self.ui.update()
        print("display updated")
        await self.api.create_session()

    async def record(self) -> None:
        """
        Controller logic step
        """
        self.ui.load_vue(
            RecordVue()
        )

        while not self._check_click():
            await asyncio.sleep(0.1)

        self.ui.dispatch_event(Event("start"))

        while not self._check_click():
            # Collect and save IMU data on buffer
            sample = self.imu.read_sample()
            self.buffer.register_sample(sample)

            # Send buffer if it is time to do so
            if self.imu.buffer.count >= self._max_imu_buffer_size:
                self.api.sen
                await self.api.send_buffer(self.buffer)
                total_time = time.ticks_diff(round(self._now()), start_time) / 1000
                print(f"[TIME] Sending time: {total_time}")
                self.buffer.clear()
            
            await asyncio.sleep(1)
