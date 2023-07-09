import xbee_frame

COORDINATOR_ADDRESS = "0x0000000000000000"

def get_data_offset(data: bytes, escaped: bool) -> int:
    """Return offset to start of frame data."""
    # Unescaped frame:
    if not escaped:
        return 3
    # Escaped data:
    # Start at first data length byte.
    offset = 1
    if data[offset] == xbee_frame.UNPACKED_ESCAPE_BYTE:
        # Skip escape byte.
        offset += 1
    # Move to 2nd data length byte.
    offset += 1
    if data[offset] == xbee_frame.UNPACKED_ESCAPE_BYTE:
        # Skip escape byte.
        offset += 1
    # Next byte after data length bytes.
    return offset + 1


def should_escape(next_byte: int) -> bool:
    """Whether the byte needs to be escaped."""
    b = bytes([next_byte])
    return b == xbee_frame.START_BYTE or \
           b == xbee_frame.ESCAPE_BYTE or \
           b == xbee_frame.XON_BYTE or \
           b == xbee_frame.XOFF_BYTE


def escape_byte(next_byte: int) -> int:
    """Escape (or unescape) a byte."""
    return next_byte ^ 0x20


def append_with_escape(next_byte: int, data: bytes, escaped: bool) -> bytes:
    """Append next byte, if needed."""
    if escaped and should_escape(next_byte):
        data += xbee_frame.ESCAPE_BYTE
        data += bytes([escape_byte(next_byte)])
    else:
        data += bytes([next_byte])
    return data


def calculate_checksum(data: bytes, escaped: bool) -> int:
    """Calculate frame checksum."""
    data_offset = get_data_offset(data, escaped)
    total = 0
    next_byte_escaped = False
    for i in range(data_offset, len(data)):
        if escaped and data[i] == xbee_frame.UNPACKED_ESCAPE_BYTE:
            next_byte_escaped = True
            continue
        if next_byte_escaped:
            next_byte_escaped = False
            total += escape_byte(data[i])
        else:
            total += data[i]
    checksum = 0xFF & total
    checksum = 0xFF & (0XFF - checksum)
    return checksum


def validate_checksum(data: bytes, escaped: bool) -> bool:
    """Validate trailing checksum value."""
    checksum = calculate_checksum(data[:-1], escaped)
    return checksum == data[-1]


def create_transmit_frame(address: str, frame_id: int, tx_data: bytes, escaped: bool) -> xbee_frame.XbeeFrame:
    """Generate a transmit frame with text payload.
       The enabled parameter corresponds to API Enable AP=1 (False) or AP=2 (True).
    """
    # Address expected format: 0x0001020304050607.
    # Create transmit packet:
    data_len = 0
    data = b''
    # packet type
    data += bytes([xbee_frame.FRAME_TYPE_TRANSMIT])
    data_len += 1
    # frame id
    data += bytes([frame_id])
    data_len += 1
    # long address (skip leading 0x)
    for b in range(2, 18, 2):
        data = append_with_escape(int(address[b] + address[b + 1], 16), data, escaped)
        data_len += 1
    # network address
    data += b'\xFF'
    data += b'\xFE'
    data_len += 2
    # broadcast radius
    data += b'\x00'
    data_len += 1
    # tx options
    data += b'\x00'
    data_len += 1
    # data at offset 17 bytes
    for next_byte in tx_data:
        data = append_with_escape(next_byte, data, escaped)
        data_len += 1
    # Fill leading and remaining frame bytes:
    prefix = xbee_frame.START_BYTE
    # big endian data length
    data_len_hi = 0xff & (data_len >> 8)
    data_len_lo = 0xff & data_len
    prefix = append_with_escape(data_len_hi, prefix, escaped)
    prefix = append_with_escape(data_len_lo, prefix, escaped)
    data = prefix + data
    checksum = calculate_checksum(data, escaped)
    data = append_with_escape(checksum, data, escaped)
    return xbee_frame.XbeeFrame(data, escaped=escaped)
