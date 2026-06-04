from app.models.exceptions import InvalidIMUPayloadError

from dataclasses import dataclass, field
from functools import cached_property

import struct



@dataclass(frozen=True)
class IMUSample:
    ax: float
    ay: float
    az: float
    gz: float


class IMUBinaryCodec:
    HEADER_FMT = "<HIH"    # window_id (u16), timestamp_start (u32), count (u16)
    SAMPLE_FMT = "<4f"     # ax, ay, az, gz
    HEADER_SIZE = struct.calcsize(HEADER_FMT)
    SAMPLE_SIZE = struct.calcsize(SAMPLE_FMT)

    @classmethod
    def decode_header(cls, payload: bytes) -> tuple[int, int, int]:
        """
        Decode IMU payload header.

        Args:
            payload (bytes): Full binary payload (header + samples)

        Returns:
            tuple[int, int, int]: (window_id, timestamp_start, count)
        """
        if len(payload) < cls.HEADER_SIZE:
            raise InvalidIMUPayloadError(
                f"Payload too short for header: {len(payload)} < {cls.HEADER_SIZE}"
            )

        return struct.unpack_from(cls.HEADER_FMT, payload, 0)

    @classmethod
    def expected_payload_size(cls, count: int) -> int:
        """
        Compute expected payload size from sample count.

        Args:
            count (int): Number of IMU samples in payload

        Returns:
            int: Expected total payload size
        """
        return cls.HEADER_SIZE + count * cls.SAMPLE_SIZE


@dataclass(frozen=True)
class IMUBuffer:
    """
    Immutable IMU buffer decoded from raw binary payload.

    Access decoded values via computed properties:
      - window_id
      - timestamp_start
      - count
      - samples
    """
    binary: bytes = field(repr=False)
    session_id: str

    def __post_init__(self) -> None:
        """
        Validate binary payload format at instantiation time.

        Raises:
            InvalidIMUPayloadError: If payload size or structure is invalid
        """
        if len(self.binary) < IMUBinaryCodec.HEADER_SIZE:
            raise InvalidIMUPayloadError(
                f"Payload too short: got={len(self.binary)}, "
                f"min={IMUBinaryCodec.HEADER_SIZE}"
            )

        _, _, count = IMUBinaryCodec.decode_header(self.binary)
        expected_size = IMUBinaryCodec.expected_payload_size(count)

        if len(self.binary) != expected_size:
            raise InvalidIMUPayloadError(
                f"Invalid payload size: got={len(self.binary)}, "
                f"expected={expected_size}, count={count}"
            )

    @cached_property
    def _header(self) -> tuple[int, int, int]:
        """
        Decode header once and cache it.

        Returns:
            tuple[int, int, int]: (window_id, timestamp_start, count)
        """
        return IMUBinaryCodec.decode_header(self.binary)

    @property
    def window_id(self) -> int:
        """
        Get window ID from header.

        Returns:
            int: Window ID
        """
        return self._header[0]

    @property
    def timestamp_start(self) -> int:
        """
        Get start timestamp from header.

        Returns:
            int: Start timestamp (u32)
        """
        return self._header[1]

    @property
    def count(self) -> int:
        """
        Get sample count from header.

        Returns:
            int: Number of samples
        """
        return self._header[2]

    @cached_property
    def samples(self) -> list[IMUSample]:
        """
        Decode samples once and cache them.

        Returns:
            tuple[IMUSample]: Decoded IMU samples
        """
        decoded: list[IMUSample] = []
        offset = IMUBinaryCodec.HEADER_SIZE

        for _ in range(self.count):
            ax, ay, az, gz = struct.unpack_from(IMUBinaryCodec.SAMPLE_FMT, self.binary, offset)
            decoded.append(IMUSample(ax=ax, ay=ay, az=az, gz=gz))
            offset += IMUBinaryCodec.SAMPLE_SIZE

        return decoded