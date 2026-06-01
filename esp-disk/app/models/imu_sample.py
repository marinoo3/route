import struct
import time


class IMUSample:

    def __init__(
            self,
            t_us: int,
            ax: float,
            ay: float,
            az: float,
            gx: float,
            gy: float,
            gz: float,
            temp_c: float
        ) -> None:
        self.t_us = t_us
        self.ax = ax
        self.ay = ay
        self.az = az
        self.gx = gx
        self.gy = gy
        self.gz = gz
        self.temp_c = temp_c

class IMUSamplesBuffer:

    def __init__(
            self,
            window_id: int = 0,
            max_size: int = 250
            ) -> None:
        self.window_id = window_id
        self.max_size = max_size
        self._count = 0
        self._data = bytearray(IMUBinaryCodec.SAMPLE_SIZE * max_size)
        self.timestamp_start = time.ticks_ms()

    @property
    def count(self) -> int:
        return self._count

    def register_sample(self, sample: IMUSample) -> None:
        """
        Pack sample directly into the pre-allocated buffer — no heap object retained.
        When full, new samples overwrite from the start (ring buffer).
        """
        idx = self._count % self.max_size
        struct.pack_into(
            IMUBinaryCodec.SAMPLE_FMT,
            self._data,
            idx * IMUBinaryCodec.SAMPLE_SIZE,
            sample.t_us, sample.ax, sample.ay, sample.az,
            sample.gx, sample.gy, sample.gz, sample.temp_c
        )
        if self._count < self.max_size:
            self._count += 1

    def to_binary(self) -> bytearray:
        """
        Encode buffer to binary payload — header + packed samples.

        Returns:
            bytearray: Binary payload ready to send
        """
        count = self._count
        data_len = count * IMUBinaryCodec.SAMPLE_SIZE
        out = bytearray(IMUBinaryCodec.HEADER_SIZE + data_len)
        struct.pack_into(
            IMUBinaryCodec.HEADER_FMT,
            out, 0,
            self.window_id, self.timestamp_start, count
        )
        out[IMUBinaryCodec.HEADER_SIZE:] = self._data[:data_len]
        return out

    def clear(self) -> None:
        """
        Reset buffer — O(1), no allocation, no GC pressure.
        """
        self._count = 0
        self.timestamp_start = time.ticks_ms()
        self.window_id += 1


class IMUBinaryCodec:
    HEADER_FMT = "<IIH"      # window_id, timestamp_start, sample_count
    SAMPLE_FMT = "<I7f"      # t_us, ax, ay, az, gx, gy, gz, temp_c
    HEADER_SIZE = struct.calcsize(HEADER_FMT)
    SAMPLE_SIZE = struct.calcsize(SAMPLE_FMT)

    def payload_size(self, sample_count: int) -> int:
        """
        Compute payload size in bytes for a number of samples.

        Args:
            sample_count (int): Number of IMU samples

        Returns:
            int: Total payload size in bytes
        """
        return self.HEADER_SIZE + sample_count * self.SAMPLE_SIZE

