from app.libs.async_urequests import arequests
import uasyncio



async def func():
    response = await arequests.get("http://172.20.10.4:8000/ping")
    print(response)

uasyncio.run(func())



