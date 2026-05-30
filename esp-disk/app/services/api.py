from models import IMUSamplesBuffer, APIQueueRequest

import _thread
import time
import urequests


class API:
    """
    API service responsible for sending data to remote endpoints using a background thread.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        device_id: str,
        timeout_s: int = 8,
        max_queue_size: int = 1,
        retry_count: int = 2,
    ) -> None:
        """
        Initialize API service.

        Args:
            base_url (str): API base URL
            api_key (str): API authentication key
            device_id (str): Unique device identifier
            timeout_s (int): HTTP timeout in seconds
            max_queue_size (int): Max queued requests
            retry_count (int): Number of retries on failure
        """
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._device_id = device_id
        self._timeout_s = timeout_s
        self._max_queue_size = max_queue_size
        self._retry_count = retry_count

        self._queue: list[APIQueueRequest] = []
        self._queue_lock = _thread.allocate_lock()

        self._running = False
        self._last_prediction: str|None = None
        self._prediction_lock = _thread.allocate_lock()

    def start(self) -> None:
        """
        Start background worker thread.

        Returns:
            None
        """
        if self._running:
            return

        self._running = True
        _thread.start_new_thread(self._worker_loop, ())

    def stop(self) -> None:
        """
        Stop background worker thread.

        Returns:
            None
        """
        self._running = False

    def send_buffer(self, samples: IMUSamplesBuffer) -> bool:
        """
        Enqueue a batch upload request.

        Args:
            samples (IMUSamplesBuffer): IMU samples batch

        Returns:
            bool: True if request was queued, False if queue is full
        """
        payload = {
            "api_key": self._api_key,
            "device_id": self._device_id,
            "timestamp_start": samples.timestamp_start,
            "data": samples.to_binary(),
        }
        return self._enqueue(
            APIQueueRequest("/upload", payload, "upload")
        )

    def predict(self, samples: IMUSamplesBuffer) -> bool:
        """
        Enqueue a prediction request.

        Args:
            samples (IMUSamplesBuffer): IMU samples batch

        Returns:
            bool: True if request was queued, False if queue is full
        """
        payload = {
            "api_key": self._api_key,
            "device_id": self._device_id,
            "window_id": samples.window_id,
            "samples": samples.values,
        }

        return self._enqueue(
            APIQueueRequest("/predict", payload, "predict")
        )

    def get_last_prediction(self) -> str|None:
        """
        Read latest prediction result.

        Returns:
            str: Last prediction payload or None
        """
        with self._prediction_lock:
            return self._last_prediction

    def _enqueue(self, request: APIQueueRequest) -> bool:
        """
        Add request to internal queue.

        Args:
            endpoint (str): API endpoint path
            payload (dict): POST body
            kind (Literal["upload", "predict"]): Request type label ("upload" or "predict")

        Returns:
            bool: True if queued, False if queue is full
        """
        with self._queue_lock:
            if len(self._queue) >= self._max_queue_size:
                return False
            self._queue.append(request)
            return True

    def _pop(self) -> APIQueueRequest|None:
        """
        Pop next request from queue.

        Returns:
            APIQueueRequest, optional: Next queued request or None
        """
        with self._queue_lock:
            if not self._queue:
                return None
            return self._queue.pop(0)

    def _worker_loop(self) -> None:
        """
        Background loop that processes queued HTTP requests.

        Returns:
            None
        """
        while self._running:
            request = self._pop()
            if request is None:
                time.sleep_ms(50)
                continue

            response_data = self._post_with_retry(request.endpoint, request.payload)

            if request.kind == "predict" and response_data is not None:
                with self._prediction_lock:
                    self._last_prediction = response_data['route']

    def _post_with_retry(self, endpoint: str, payload: dict) -> dict|None:
        """
        Send HTTP POST with retry logic.

        Args:
            endpoint (str): API endpoint path
            payload (dict: JSON body

        Returns:
            dict, optional: Response JSON on success, None on failure
        """
        url = self._base_url + endpoint

        for attempt in range(self._retry_count + 1):
            response = None
            try:
                response = urequests.post(url, json=payload, timeout=self._timeout_s)
                if 200 <= response.status_code < 300:
                    try:
                        data = response.json()
                    except Exception:
                        data = {"status": "ok"}
                    return data
            except Exception:
                pass
            finally:
                if response is not None:
                    response.close()

            if attempt < self._retry_count:
                time.sleep_ms(200)

        return None