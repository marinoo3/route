"""
urequests.py – CPython-compatible shim for MicroPython's urequests module.

Usage pattern in application code:

    try:
        import urequests               # ESP32
    except ImportError:
        import urequests_desktop as urequests

    r = urequests.get("https://httpbin.org/get",
                      headers={"User-Agent": "esp32"})
    print(r.status_code, r.text)
    r.close()
"""

from __future__ import annotations
from typing import Any, Dict, Iterable, Iterator, Optional

import requests  # pip install requests


__all__ = [
    "request",
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "head",
    "Response",
]


class Response:
    """
    Minimal MicroPython-compatible response wrapper.

    Properties:
        text        -> unicode body (decoded via requests' encoding logic)
        content     -> raw bytes
        status_code -> HTTP status integer
        reason      -> status text
        headers     -> dict-like
    Methods:
        close()     -> release underlying connection
        json()      -> parse JSON body (calls requests.Response.json)
        iter_content(chunk_size) -> iterator yielding bytes chunks
    """

    def __init__(self, resp: requests.Response):
        self._resp = resp
        self.raw = resp.raw   # MicroPython exposes .raw sometimes
        self.status_code = resp.status_code
        self.reason = resp.reason
        self.headers = resp.headers

    def close(self) -> None:
        self._resp.close()

    @property
    def content(self) -> bytes:
        return self._resp.content

    @property
    def text(self) -> str:
        return self._resp.text

    def json(self) -> Any:
        return self._resp.json()

    def iter_content(self, chunk_size: int = 1024) -> Iterator[bytes]:
        return self._resp.iter_content(chunk_size=chunk_size)

    def __enter__(self) -> "Response":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


def request(
    method: str,
    url: str,
    data: Any = None,
    json: Any = None,
    headers: Optional[Dict[str, str]] = None,
    stream: bool = False,
    **kwargs: Any,
) -> Response:
    """
    Core request function – mirrors MicroPython's urequests.request.

    Additional kwargs (timeout, auth, params, etc.) are forwarded to
    the CPython `requests` implementation.
    """
    resp = requests.request(
        method=method,
        url=url,
        data=data,
        json=json,
        headers=headers,
        stream=stream,
        **kwargs,
    )
    return Response(resp)


def get(url: str, **kwargs: Any) -> Response:
    return request("GET", url, **kwargs)


def post(url: str, **kwargs: Any) -> Response:
    return request("POST", url, **kwargs)


def put(url: str, **kwargs: Any) -> Response:
    return request("PUT", url, **kwargs)


def patch(url: str, **kwargs: Any) -> Response:
    return request("PATCH", url, **kwargs)


def delete(url: str, **kwargs: Any) -> Response:
    return request("DELETE", url, **kwargs)


def head(url: str, **kwargs: Any) -> Response:
    return request("HEAD", url, **kwargs)