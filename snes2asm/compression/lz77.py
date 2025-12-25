"""
LZ77 compression and decompression

Standard LZ77 sliding window compression suitable for SNES ROMs.
Uses a sliding window to find repeated sequences and encodes them as
(offset, length) pairs.

Format:
- Control byte: 8 bits indicating literal (0) or reference (1) for next 8 blocks
- Literal: 1 byte of uncompressed data
- Reference: 2 bytes encoding (offset, length)
  - 12 bits for offset (0-4095)
  - 4 bits for length (3-18, encoded as length-3)
"""

def compress(data):
    """
    Compress data using LZ77 algorithm.

    Args:
        data: bytes-like object to compress

    Returns:
        bytes: compressed data
    """
    if isinstance(data, (bytes, bytearray)):
        data = bytes(data)
    else:
        raise TypeError("data must be bytes or bytearray")

    if len(data) == 0:
        return bytes()

    # Configuration
    WINDOW_SIZE = 4096  # 12-bit offset
    MIN_MATCH = 3       # Minimum match length
    MAX_MATCH = 18      # Maximum match length (3 + 15)

    output = bytearray()
    pos = 0

    while pos < len(data):
        # Buffer for the next 8 blocks (literals or references)
        blocks = []
        control_byte = 0

        for bit_pos in range(8):
            if pos >= len(data):
                break

            # Search for matches in the sliding window
            window_start = max(0, pos - WINDOW_SIZE)
            best_match_offset = 0
            best_match_length = 0

            # Look for the longest match
            for offset in range(window_start, pos):
                # Calculate offset (distance back from current position)
                match_offset = pos - offset

                # Skip if offset doesn't fit in 12 bits (max 4095)
                if match_offset >= WINDOW_SIZE:
                    continue

                match_length = 0
                while (match_length < MAX_MATCH and
                       pos + match_length < len(data) and
                       data[offset + match_length] == data[pos + match_length]):
                    match_length += 1

                if match_length >= MIN_MATCH and match_length > best_match_length:
                    best_match_length = match_length
                    best_match_offset = match_offset

            # Decide whether to use literal or reference
            if best_match_length >= MIN_MATCH:
                # Use reference (set bit to 1)
                control_byte |= (1 << bit_pos)

                # Encode offset (12 bits) and length (4 bits)
                # Length is stored as (actual_length - 3) since minimum is 3
                encoded = (best_match_offset & 0x0FFF) | ((best_match_length - MIN_MATCH) << 12)

                # Store as little-endian 16-bit value
                blocks.append(bytes([encoded & 0xFF, (encoded >> 8) & 0xFF]))
                pos += best_match_length
            else:
                # Use literal (bit is already 0)
                blocks.append(bytes([data[pos]]))
                pos += 1

        # Write control byte followed by blocks
        output.append(control_byte)
        for block in blocks:
            output.extend(block)

    return bytes(output)


def decompress(data):
    """
    Decompress LZ77 compressed data.

    Args:
        data: bytes-like object containing compressed data

    Returns:
        bytes: decompressed data
    """
    if isinstance(data, (bytes, bytearray)):
        data = bytes(data)
    else:
        raise TypeError("data must be bytes or bytearray")

    if len(data) == 0:
        return bytes()

    MIN_MATCH = 3
    output = bytearray()
    pos = 0

    while pos < len(data):
        # Read control byte
        control_byte = data[pos]
        pos += 1

        # Process 8 blocks
        for bit_pos in range(8):
            if pos >= len(data):
                break

            if control_byte & (1 << bit_pos):
                # Reference: read 2-byte encoded value
                if pos + 1 >= len(data):
                    break

                encoded = data[pos] | (data[pos + 1] << 8)
                pos += 2

                # Decode offset and length
                offset = encoded & 0x0FFF
                length = ((encoded >> 12) & 0x0F) + MIN_MATCH

                # Copy from sliding window
                copy_start = len(output) - offset

                # Validate offset is within bounds
                if copy_start < 0:
                    # Invalid offset, stop decompression
                    return bytes(output)

                # Handle overlapping copies (e.g., run-length encoding)
                # For overlapping copies, we read and append one byte at a time
                # This allows reading from positions we just wrote
                for i in range(length):
                    read_pos = copy_start + i
                    # Check if we're reading beyond available data
                    # This can happen with malformed compressed data
                    if read_pos >= len(output):
                        break
                    output.append(output[read_pos])
            else:
                # Literal: copy byte directly
                output.append(data[pos])
                pos += 1

    return bytes(output)
