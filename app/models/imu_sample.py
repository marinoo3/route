


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
            values: list[IMUSample],
            window_id: int,
            timestamp_start: int
            ) -> None:
        self.values = values
        self.window_id = window_id
        self.timestamp_start = timestamp_start