import unittest
from mocks import MockUart
import xbee_frame
import xbee_frame_builder as builder
from xbee_serial import XbeeSerial

class TestXbeeSerial(unittest.TestCase):

    def test_receive_unescaped(self):
        packet = bytes([0x7E, 0x00, 0x1E, 0x90, 0x00, 0x14, 0xA1, 0x00, 0x40, 0xC3, 0x54,
                            0x9D, 0xF1, 0xA8, 0x02, 0x43, 0x3D, 0x32, 0x34, 0x2E, 0x39, 0x30, 0x26, 0x50,
                            0x3D, 0x31, 0x30, 0x32, 0x37, 0x2E, 0x36, 0x36, 0x0D, 0x8A])
        uart = MockUart(packet)
        xbs = XbeeSerial(uart, escaped=False)
        frame = xbs.receive()
        assert(frame is not None)
        # Should be unescaped
        assert(not frame.Escaped)
        assert(frame.Data == packet)
        assert(frame.get_frame_type() == xbee_frame.FRAME_TYPE_RECEIVE)
        assert(frame.get_receive_data().decode() == "C=24.90&P=1027.66\r")
        assert(frame.get_source_address() == "0x0014A10040C3549D")
        assert(builder.validate_checksum(frame.Data, frame.Escaped))

    def test_receive_escaped(self):
        packet = bytes([0x7E, 0x00, 0x7D, 0x31, 0x90, 0x00, 0x7D, 0x33, 0xA2, 0x00,
                        0x40, 0x79, 0xF9, 0xE1, 0xFF, 0xFE, 0x01, 0x62, 0x6C, 0x69, 0x6E, 0x6B, 0x19])
        uart = MockUart(packet)
        xbs = XbeeSerial(uart, escaped=True)
        frame = xbs.receive()
        assert(frame is not None)
        # Should be unescaped.
        assert(not frame.Escaped)
        assert(frame.Data != packet)
        assert(frame.Data == b'~\x00\x11\x90\x00\x13\xa2\x00@y\xf9\xe1\xff\xfe\x01blink\x19')
        assert(frame.get_frame_type() == xbee_frame.FRAME_TYPE_RECEIVE)
        assert(builder.validate_checksum(frame.Data, frame.Escaped))

if __name__ == "__main__":
    unittest.main()
