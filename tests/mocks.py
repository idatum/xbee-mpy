
class MockUart():
    def __init__(self, data: bytes):
        self._data = data
        self._pos = 0

    def read(self, _: int) -> int:
        """Read 1 byte."""
        next_byte = bytes([self._data[self._pos]])
        self._pos += 1
        return next_byte
