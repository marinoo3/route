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
        self.values: list[IMUSample] = []
        self.timestamp_start = time.ticks_ms()
        self.binary_codec = IMUBinaryCodec()

    def register_sample(self, sample: IMUSample) -> None:
        """
        Add a sample to the buffer

        Args:
            sample (IMUSample): Sample to add
        """
        self.values.append(sample)
        # Remove first element if buffer to large
        if len(self.values) > self.max_size:
            self.values.pop(0)

    def to_binary(self) -> bytes:
        """
        Encode buffer values to binary payload

        Returns:
            bytes: Binary payload ready to send
        """
        return self.binary_codec.encode(self)
    
    def clear(self) -> None:
        """
        Clear buffer, set timestamp_start to current time and increase window_id to 1
        """
        self.values.clear()
        self.timestamp_start = time.ticks_ms()
        self.window_id += 1


class IMUBinaryCodec:
    HEADER_FMT = "<IIH"      # window_id, timestamp_start, sample_count
    SAMPLE_FMT = "<I7f"      # t_us, ax, ay, az, gx, gy, gz, temp_c

    def payload_size(self, sample_count: int) -> int:
        """
        Compute payload size in bytes for a number of samples.

        Args:
            sample_count (int): Number of IMU samples

        Returns:
            int: Total payload size in bytes
        """
        header_size = struct.calcsize(self.HEADER_FMT)
        sample_size = struct.calcsize(self.SAMPLE_FMT)
        return header_size + sample_count * sample_size

    def encode(self, buffer: IMUSamplesBuffer) -> bytes:
        """
        Encode IMUSamplesBuffer to binary payload.

        Args:
            buffer (IMUSamplesBuffer): Buffer to encode

        Returns:
            bytes: Binary payload ready to send
        """
        count = len(buffer.values)
        total_size = self.payload_size(count)
        out = bytearray(total_size)

        offset = 0
        struct.pack_into(
            self.HEADER_FMT,
            out,
            offset,
            buffer.window_id,
            buffer.timestamp_start,
            count
        )
        offset += struct.calcsize(self.HEADER_FMT)

        i = 0
        while i < count:
            s = buffer.values[i]
            struct.pack_into(
                self.SAMPLE_FMT,
                out,
                offset,
                s.t_us,
                s.ax,
                s.ay,
                s.az,
                s.gx,
                s.gy,
                s.gz,
                s.temp_c
            )
            offset += struct.calcsize(self.SAMPLE_FMT)
            i += 1

        return bytes(out)

