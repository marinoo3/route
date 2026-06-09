# This file is executed on every boot (including wake-boot from deepsleep)
# boot.py
import network
import time

CONNECT_TIMEOUT = 3
CHECK_INTERVAL = 0.5

def reset_sta():
    sta = network.WLAN(network.STA_IF)
    sta.active(False)
    time.sleep(1)
    sta.active(True)
    return sta

def connect_wifi(ssid: str, pwd: str):
    ap = network.WLAN(network.AP_IF)
    ap.active(False)

    sta = reset_sta()

    if sta.isconnected():
        print("Déjà connecté :", sta.ifconfig())
        return True

    try:
        print("Connexion à", ssid)
        sta.connect(ssid, pwd)

        deadline = time.time() + CONNECT_TIMEOUT
        while not sta.isconnected() and time.time() < deadline:
            time.sleep(CHECK_INTERVAL)

        if sta.isconnected():
            print("Connecté :", sta.ifconfig())
            return True

        sta.disconnect()
        time.sleep(1)

    except OSError as err:
        print("Erreur Wi-Fi :", err)
        sta.disconnect()
        time.sleep(2)

    return False

