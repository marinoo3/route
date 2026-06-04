from app.models import IMUSamplesBuffer
from app.models.exceptions import APIError
from app.models.imu_sample import IMUBinaryCodec
from app import log

import time
import urequests


class SimpleAPI:
    """
    Blocking API service — no threads, no queue. Each call blocks until complete.
    Use for debugging or when IMU data loss during HTTP is acceptable.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        device_id: str,
        timeout_s: int = 8,
        retry_count: int = 2,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._device_id = device_id
        self._timeout_s = timeout_s
        self._retry_count = retry_count
        self._session_id: str | None = None
        self._last_prediction: str | None = None
        
    def start(self):
        print("Start dummy API thread")
    
    def stop(self):
        print("stopped dummy API thread")

    def create_session(self) -> str:
        payload = {
            "api_key": self._api_key,
            "device_id": self._device_id,
        }
        content = self._post_with_retry("/create_session", payload)
        if not content:
            raise APIError("Failed to create a route session")
        self._session_id = content["session_id"]
        return self._session_id

    def send_buffer(self, samples: IMUSamplesBuffer) -> bool:
        payload = bytes(samples.to_binary())  # force immutable raw bytes
        url = self._base_url + f"/register_route_buffer?session_id={self._session_id}"
        headers = {
            "Content-Type": "application/octet-stream",
            "Content-Length": str(len(payload)),
        }
        
        print("HEADER_FMT", IMUBinaryCodec.HEADER_FMT)
        print("HEADER_SIZE", IMUBinaryCodec.HEADER_SIZE)
        print("SAMPLE_SIZE", IMUBinaryCodec.SAMPLE_SIZE)
        payload = samples.to_binary()
        print("payload_len", len(payload))
        print("payload_head_hex", bytes(payload[:24]).hex())

        response = urequests.post(
            url,
            data=payload,   # body = raw binary bytes
            timeout=self._timeout_s,
            headers=headers,
        )

        return response.status_code == 200

    def predict(self, samples: IMUSamplesBuffer) -> str | None:
        payload = {
            "session_id": self._session_id,
            "window_id": samples.window_id,
            "samples": samples.values,
        }
        content = self._post_with_retry("/predict", payload)
        if content is not None:
            self._last_prediction = content.get("route")
        return self._last_prediction

    def get_last_prediction(self) -> str | None:
        return self._last_prediction

    def _post_with_retry(
            self, 
            endpoint: str, 
            payload: dict, 
            headers: dict|None = None
        ) -> dict | None:

        url = self._base_url + endpoint

        for attempt in range(self._retry_count + 1):
            response = None
            try:
                log(url)
                response = urequests.post(
                    url, 
                    json=payload,
                    timeout=self._timeout_s,
                    headers=headers
                )
                if 200 <= response.status_code < 300:
                    try:
                        data = response.json()
                    except Exception:
                        data = {"status": "ok"}
                    return data
            except Exception as e:
                log(e)
            finally:
                if response is not None:
                    response.close()

            if attempt < self._retry_count:
                time.sleep_ms(200)

        return None



