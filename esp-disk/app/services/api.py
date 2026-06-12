from config import PUSH_FRECENCY_SEC, API_MAX_QUEUE_SIZE
from app.models import IMUSamplesBuffer, APIRequest
from app.models.exceptions import APIError
from app import log

import uasyncio as asyncio
from app.libs.async_urequests import arequests


class API:
    """
    Async API service — all HTTP calls are coroutines, no blocking, no threads.
    Designed to run inside a uasyncio event loop.
    """
    _session_id: str | None
    _queue: list[APIRequest]

    def __init__(
        self,
        base_url: str,
        api_key: str,
        device_id: str,
        timeout_s: int = 8,
        retry_count: int = 2,
    ) -> None:
        """
        Initialize AsyncAPI service.

        Args:
            base_url (str): API base URL
            api_key (str): API authentication key
            device_id (str): Unique device identifier
            timeout_s (int): HTTP timeout in seconds
            retry_count (int): Number of retries on failure
        """
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._device_id = device_id
        self._timeout_s = timeout_s
        self._retry_count = retry_count

        self._push_frequency_sec = PUSH_FRECENCY_SEC
        self._max_queue_size = API_MAX_QUEUE_SIZE

    def _queue_request(self, request: APIRequest) -> bool:
        """
        Queue a post request

        Args:
            request (APIRequest): Request to queue

        Returns:
            bool: Was the request queued
        """
        if len(self._queue) > self._push_frequency_sec:
            self._queue.append(request)
            return True
        
        return False

    async def create_session(self) -> None:
        """
        Add session creation event in queue
        """
        content = await self._post_with_retry(
            "/create_session",
            json={
                "api_key": self._api_key,
                "device_id": self._device_id,
            }
        )

        if not content or not content.get('session_id'):
            raise APIError("Failed to create a route session")
        
        self._session_id = content['session_id']

    def send_buffer(self, samples: IMUSamplesBuffer) -> None:
        """
        Add buffer send event in API queue:
        Send a binary IMU buffer to the server.

        Args:
            samples (IMUSamplesBuffer): IMU samples batch to upload
        """
        payload = bytes(samples.to_binary())

        request = APIRequest(
            endpoint=f"/register_route_buffer?session_id={self._session_id}",
            headers = {
                "Content-Type": "application/octet-stream",
                "Content-Length": str(len(payload)),
            }
        )

        self._queue_request(request)

    async def run(self) -> APIRequest:
        """
        Continuously send API requests if in queue
        """
        while True:
            request = self._queue.pop(0)
            if not request:
                await asyncio.sleep(0.1)
                continue
            
            content = await self._post_with_retry(request.endpoint, headers=request.headers, json=request.json, data=request.data)
            
            if request.post_action:
                request.post_action(content)

    async def _post_with_retry(
        self,
        endpoint: str,
        headers: dict | None = None,
        json: dict | None = None,
        data: bytes | None = None,
    ) -> dict | None:
        """
        Send an async HTTP POST with retry logic.

        Args:
            endpoint (str): API endpoint path
            headers (dict, optional): Additional HTTP headers
            json (dict, optional): JSON body — mutually exclusive with data
            data (bytes, optional): Raw binary body — mutually exclusive with json

        Returns:
            dict | None: Parsed response JSON on success, None on failure
        """
        url = self._base_url + endpoint

        for attempt in range(self._retry_count + 1):
            response = None
            try:
                log(url)
                response = await arequests.post(
                    url,
                    headers=headers or {},
                    json=json,
                    data=data,
                    timeout=self._timeout_s,
                )
                if 200 <= response.status_code < 300:
                    try:
                        return response.json()
                    except Exception:
                        return {"status": "ok"}
            except Exception as e:
                log(e)
            finally:
                if response is not None:
                    response.close()

            if attempt < self._retry_count:
                await asyncio.sleep_ms(200)

        return None

