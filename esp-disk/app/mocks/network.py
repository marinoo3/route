"""
network.py - host mock of MicroPython's network module (WLAN station/AP).

The unix port has no `network` module.  This mock implements just enough of the
WLAN API used by app/scripts/wifi.py and boot.py to let the Wi-Fi connect flow
succeed on the host: a station interface that reports "connected" ~1.5 s after
connect() is called, returning a loopback ifconfig tuple.
"""

import time

# How long the mock takes to "associate" after connect() (1-2 s feel).
CONNECT_DELAY_MS = 1500

# Interface ids
STA_IF = 0
AP_IF = 1

# Connection status codes (ESP32-style)
STAT_IDLE = 0
STAT_CONNECTING = 1
STAT_WRONG_PASSWORD = -3
STAT_NO_AP_FOUND = -2
STAT_CONNECT_FAIL = -1
STAT_GOT_IP = 3


class WLAN:
    def __init__(self, interface=STA_IF):
        self._interface = interface
        self._active = False
        self._connected = False
        self._connect_at = None
        self._ssid = None

    def active(self, is_active=None):
        if is_active is None:
            return self._active
        self._active = bool(is_active)
        if not self._active:
            self._connected = False
        return self._active

    def connect(self, ssid=None, password=None, **kwargs):
        # Host mock: the association "succeeds" CONNECT_DELAY_MS after connect()
        # so the boot screen shows a realistic 1-2 s connecting phase.
        self._ssid = ssid
        self._connected = False
        self._connect_at = time.ticks_ms()

    def disconnect(self):
        self._connected = False
        self._connect_at = None

    def isconnected(self):
        if not self._connected and self._connect_at is not None:
            if time.ticks_diff(time.ticks_ms(), self._connect_at) >= CONNECT_DELAY_MS:
                self._connected = True
        return self._connected

    def status(self, param=None):
        if param == "rssi":
            return -50
        return STAT_GOT_IP if self._connected else STAT_IDLE

    def ifconfig(self, config=None):
        if config is not None:
            return None
        # (ip, subnet, gateway, dns)
        return ("127.0.0.1", "255.255.255.0", "127.0.0.1", "127.0.0.1")

    def config(self, *args, **kwargs):
        if len(args) == 1:
            key = args[0]
            if key == "mac":
                return b"\x02\x00\x00\x00\x00\x01"
            if key in ("essid", "ssid"):
                return self._ssid or ""
            return None
        return None

    def scan(self):
        return []
