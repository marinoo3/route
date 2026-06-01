import requests
import time


def _post_with_retry(endpoint: str, payload: dict) -> dict|None:
        """
        Send HTTP POST with retry logic.

        Args:
            endpoint (str): API endpoint path
            payload (dict: JSON body

        Returns:
            dict, optional: Response JSON on success, None on failure
        """
        url = "http://0.0.0.0:8000/api/create_session"
        payload = {'device_id': '6fb12293-82c5-4121-8cae-87d78d68ce6a', 'api_key': '123'}

        for attempt in range(2 + 1):
            response = None
            try:
                
                response = requests.post(url, json=payload, timeout=8)
                if 200 <= response.status_code < 300:
                    try:
                        data = response.json()
                    except Exception:
                        data = {"status": "ok"}
                    return data
            except Exception as e:
                print(e)
            finally:
                if response is not None:
                    response.close()
                    
            if attempt < 2:
                time.sleep(200)

        return None



print(_post_with_retry("", {}))