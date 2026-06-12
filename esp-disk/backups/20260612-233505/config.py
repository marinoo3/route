# config.py


# -------- Pins

SDA_PIN: int = 21
SCL_PIN: int = 22
BTN_GPIO = 27

# -------- Hotspot

SSID = "marin iPhone"
PWD = "marinooo"

# -------- Server

API_URL: str = "http://172.20.10.4:8000/api"
API_KEY: str = "123"
PUSH_FRECENCY_SEC: int = 10

# --------- MEMORY
API_MAX_QUEUE_SIZE: int = 1
IMU_MAX_BUFFER_SIZE: int = 500

# --------- SENSOR

IMU_FREQ: float = 1/20

# -------- App

DEVICE_ID: str = "6fb12293-82c5-4121-8cae-87d78d68ce6a"
UI_REFRESH_RATE: float = 1/10
