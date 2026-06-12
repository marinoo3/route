from machine import Pin
import time

# Button between GPIO27 and GND
button = Pin(27, Pin.IN, Pin.PULL_UP)

while True:
    if button.value() == 0:   # pressed (active low)
        print("Button pressed!")
        time.sleep_ms(200)    # simple debounce / avoid spam
        while button.value() == 0:
            pass              # wait until released
    time.sleep_ms(10)