from time import sleep_us, ticks_ms

class DeviceNotReady(Exception):
    def __init__(self):
        print("Error\nHX711 is not responding")


class HX711(DeviceNotReady):
    SELA128 = const(1)
    SELB32 = const(2)
    SELA64 = const(3)
    DBITS = const(24)
    MAX_VAL = const(0x7FFFFF)
    MIN_VAL = const(0x800000)
    FRAME = const(1 << DBITS)
    READY_DELAY = const(3000)  # ms
    WAIT_SLEEP = const(60)  # us
    CHANNEL_AND_GAIN = {
        1: ("A", 128),
        2: ("B", 32),
        3: ("A", 64),
    }
    CALIBRATION_FACTOR = 1104

    def __init__(self, dOut, pdSck, ch=SELA128):
        self._data = dOut
        self._data.init(mode=self._data.IN)
        self._clk = pdSck
        self._clk.init(mode=self._clk.OUT, value=0)
        self._channel = ch
        self._tare = 0
        self._cal = HX711.CALIBRATION_FACTOR
        self.wait_ready()
        k, g = HX711.CHANNEL_AND_GAIN[ch]
        print("HX711 ready on channel {} with gain {}".format(k, g))

    def timeout(self, t):
        start = ticks_ms()
        def compare():
            return int(ticks_ms() - start) >= t
        return compare

    def is_device_ready(self):
        return self._data.value() == 0

    def wait_ready(self):
        delay_over = self.timeout(HX711.READY_DELAY)
        while not self.is_device_ready():
            if delay_over():
                raise DeviceNotReady()

    def convert_result(self, val):
        if val & HX711.MIN_VAL:
            val -= HX711.FRAME
        return val

    def clock(self):
        self._clk.value(1)
        self._clk.value(0)

    def channel(self, ch=None):
        if ch is None:
            ch, gain = HX711.CHANNEL_AND_GAIN[self._channel]
            return ch, gain
        else:
            assert ch in [1, 2, 3], "Invalid channel number: {}\nValid options are 1, 2, 3".format(ch)
            self._channel = ch
            if not self.is_device_ready():
                self.wait_ready()
            for n in range(HX711.DBITS + ch):
                self.clock()

    def get_raw(self, conv=True):
        if not self.is_device_ready():
            self.wait_ready()
        raw = 0
        for b in range(HX711.DBITS - 1):
            self.clock()
            raw = (raw | self._data.value()) << 1
        self.clock()
        raw = raw | self._data.value()
        for b in range(self._channel):
            self.clock()
        if conv:
            return self.convert_result(raw)
        else:
            return raw

    def mean(self, n):
        s = 0
        for i in range(n):
            s += self.get_raw()
        return int(s / n)

    def tare(self, n):
        self._tare = self.mean(n)
        return self._tare

    def weight(self, n):
        g = (self.mean(n) - self._tare) / self._cal
        return g

    def cal_factor(self, f=None):
        if f is not None:
            self._cal = f
        else:
            return self._cal

    def wake_up(self):
        self._clk.value(0)
        self._channel(self._channel)

    def to_sleep(self):
        self._clk.value(0)
        self._clk.value(1)
        sleep_us(HX711.WAIT_SLEEP)

