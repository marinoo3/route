# This file is executed on every boot (including wake-boot from deepsleep)
# boot.py
import network
import time

SSID = "marin iPhone"
PASSWORD = "marinooo"
CONNECT_TIMEOUT = 20
CHECK_INTERVAL = 0.5
MAX_ATTEMPTS = 2

def reset_sta():
    sta = network.WLAN(network.STA_IF)
    sta.active(False)
    time.sleep(1)
    sta.active(True)
    return sta

def connect_wifi():
    ap = network.WLAN(network.AP_IF)
    ap.active(False)

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print("Tentative", attempt)
        sta = reset_sta()

        if sta.isconnected():
            print("Déjà connecté :", sta.ifconfig())
            return True

        try:
            print("Connexion à", SSID)
            sta.connect(SSID, PASSWORD)

            deadline = time.time() + CONNECT_TIMEOUT
            while not sta.isconnected() and time.time() < deadline:
                time.sleep(CHECK_INTERVAL)

            if sta.isconnected():
                print("Connecté :", sta.ifconfig())
                return True

            print("Échec après 60 s")
            sta.disconnect()
            time.sleep(1)

        except OSError as err:
            print("Erreur Wi-Fi :", err)
            sta.disconnect()
            time.sleep(2)

    print("Toutes les tentatives ont échoué.")
    return False

connect_wifi()
