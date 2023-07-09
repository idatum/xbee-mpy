import struct
import xbee_frame

class XbeeSerial:
    """Read XBee packets from serial."""
    def __init__(self, machine_uart, escaped: bool):
        self._uart = machine_uart
        self._escaped = escaped
        self._escape_next_byte = False
        self._data = b''
        self._data_len_field = 0

    def _reset(self):
        """Reset state."""
        self._escape_next_byte = False
        self._data = b''
        self._data_len_field = 0

    def _append(self, next_byte: int) -> bool:
        """Append next byte read from serial."""
        if next_byte == xbee_frame.START_BYTE:
            self._reset()
            self._data += next_byte
            return False
        elif self._escaped and next_byte == xbee_frame.ESCAPE_BYTE:
            self._escape_next_byte = True
        elif self._escape_next_byte:
            self._escape_next_byte = False
            escaped_b = struct.unpack(">B", next_byte)[0]
            unescaped_b = struct.pack(">B", escaped_b ^ 0x20)
            self._data += unescaped_b
        else:
            self._data += next_byte
        return True

    def _frame_complete(self) -> bool:
        """Whether a complete frame has been read from serial."""
        if len(self._data) < xbee_frame.UNESCAPED_FRAME_DATA_OFFSET:
            return False
        elif self._data_len_field == 0:
            self._data_len_field = (0xff * int(self._data[1])) + int(self._data[2])
        # Drop start byte, 2 byte length, and frame type (4 bytes).
        return self._data_len_field == (len(self._data)- 4)

    def receive(self) -> xbee_frame.XbeeFrame:
        """Read from serial until a complete frame is returned."""
        while True:
            next_byte = self._uart.read(1)
            if next_byte is None:
                continue
            if not self._append(next_byte):
                continue
            if self._frame_complete():
                return xbee_frame.XbeeFrame(self._data, escaped=False)


    def transmit(self, frame: xbee_frame.XbeeFrame):
        """Send a generated XBeeFrame transmit frame type."""
        self._uart.write(frame.Data)
