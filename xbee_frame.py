
START_BYTE = b'\x7E'
ESCAPE_BYTE = b'\x7D'
XON_BYTE = b'\x11'
XOFF_BYTE = b'\x13'
FRAME_TYPE_RECEIVE = 0x90
FRAME_TYPE_TRANSMIT = 0x10
UNPACKED_ESCAPE_BYTE = 0x7D
UNESCAPED_FRAME_DATA_OFFSET = 3
UNESCAPED_RECEIVE_DATA_OFFSET = 15

class XbeeFrame:
    """Received or generated XBee frame."""
    def __init__(self, data: bytes, escaped: bool):
        self._data = data
        self._escaped = escaped

    @property
    def Data(self) -> bytes:
        """Frame data."""
        return self._data

    @property
    def Escaped(self) -> bool:
        """Whether the frame data is escaped."""
        return self._escaped
    
    def get_frame_type(self) -> int:
        """Frame packet type"""
        # Frame type is first byte in frame data.
        # Unescaped frame only.
        if self._escaped:
            return None
        return self._data[UNESCAPED_FRAME_DATA_OFFSET]

    def get_receive_data(self) -> bytes:
        """Get data field of receive packet."""
        # Unescaped frame only.
        if self.get_frame_type() != FRAME_TYPE_RECEIVE:
            return None
        # Drop last checksum byte.
        return self._data[UNESCAPED_RECEIVE_DATA_OFFSET:-1]

    def get_source_address(self) -> str:
        """Get source address of receive packet."""
        # Unescaped frame only.
        if self._escaped:
            return None
        # Receive frame only.
        if self.get_frame_type() != FRAME_TYPE_RECEIVE:
            return None
        return "0x" + "".join("{:02X}".format(b) for b in self._data[4:12])
