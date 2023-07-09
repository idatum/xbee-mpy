import unittest
import xbee_frame
import xbee_frame_builder

Escaped_tx_packet = bytes([0x7E, 0x00, 0x7D, 0x33, 0x10, 0x01,
                           0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                           0xFF, 0xFE, 0x00, 0x00, 0x62, 0x6C, 0x69, 0x6E, 0x6B, 0xE1])
Unescaped_rx_packet = bytes([0x7E, 0x00, 0x1E, 0x90, 0x00, 0x14, 0xA1, 0x00, 0x40, 0xC3, 0x54,
                            0x9D, 0xF1, 0xA8, 0x02, 0x43, 0x3D, 0x32, 0x34, 0x2E, 0x39, 0x30, 0x26, 0x50,
                            0x3D, 0x31, 0x30, 0x32, 0x37, 0x2E, 0x36, 0x36, 0x0D, 0x8A])

class TestXbeeFrame(unittest.TestCase):

    def test_escaped_data_offset(self):
        data_offset = xbee_frame_builder.get_data_offset(Escaped_tx_packet, escaped=True)
        assert(4 == data_offset)

    def test_unescaped_data_offset(self):
        data_offset = xbee_frame_builder.get_data_offset(Unescaped_rx_packet, escaped=False)
        assert(xbee_frame.UNESCAPED_FRAME_DATA_OFFSET == data_offset)

    def test_escaped_checksum(self):
        # Recalculate checksum
        checksum = xbee_frame_builder.calculate_checksum(Escaped_tx_packet[:-1], escaped=True)
        assert(0xE1 == checksum)
        assert(xbee_frame_builder.validate_checksum(Escaped_tx_packet, escaped=True))

    def test_unescaped_checksum(self):
        # Recalculate checksum
        checksum = xbee_frame_builder.calculate_checksum(Unescaped_rx_packet[:-1], escaped=False)
        assert(0x8a == checksum)
        assert(xbee_frame_builder.validate_checksum(Unescaped_rx_packet, escaped=False))

    def test_unescaped_rx_recieve_data(self):
        frame = xbee_frame.XbeeFrame(Unescaped_rx_packet, escaped=False)
        assert(b'C=24.90&P=1027.66\r' == frame.get_receive_data())

    def test_unescaped_rx_frame_type(self):
        frame = xbee_frame.XbeeFrame(Unescaped_rx_packet, escaped=False)
        assert(xbee_frame.FRAME_TYPE_RECEIVE == frame.get_frame_type())

if __name__ == "__main__":
    unittest.main()
