# -*- coding: utf-8 -*-
"""
HAL Laboratory compression/decompression (exhal/inhal format)

Based on the exhal/inhal tools by Devin Acker
Original C implementation: https://github.com/devinacker/exhal

This compression format is used in various HAL Laboratory SNES games
including Kirby's Dream Course, Kirby Super Star, and others.
"""

DATA_SIZE = 65536
RUN_SIZE = 32
LONG_RUN_SIZE = 1024

def compress(data, fast=True):
    compressor = HalCompressor(data, fast=fast)
    return compressor.compress()

def decompress(data):
    decompressor = HalDecompressor(data)
    return decompressor.decompress()

def _rotate(byte):
    """Reverse the order of bits in a byte."""
    result = 0
    if byte & 0x01: result |= 0x80
    if byte & 0x02: result |= 0x40
    if byte & 0x04: result |= 0x20
    if byte & 0x08: result |= 0x10
    if byte & 0x10: result |= 0x08
    if byte & 0x20: result |= 0x04
    if byte & 0x40: result |= 0x02
    if byte & 0x80: result |= 0x01
    return result

class HalDecompressor:
    """Decompressor for HAL Laboratory format."""

    def __init__(self, data):
        self.packed = bytearray(data)
        self.unpacked = bytearray()
        self.inpos = 0

    def decompress(self):
        """Decompress the data and return result."""
        while True:
            if self.inpos >= len(self.packed):
                break

            # Read command byte
            input_byte = self.packed[self.inpos]
            self.inpos += 1

            # Command 0xFF = end of data
            if input_byte == 0xFF:
                break

            # Check if it is a long or regular command
            if (input_byte & 0xE0) == 0xE0:
                # Long command
                command = (input_byte >> 2) & 0x07
                # Get LSB of length from next byte
                if self.inpos >= len(self.packed):
                    break
                length = (((input_byte & 0x03) << 8) | self.packed[self.inpos]) + 1
                self.inpos += 1
            else:
                # Regular command
                command = input_byte >> 5
                length = (input_byte & 0x1F) + 1

            # Execute command
            if command == 0:
                # Write uncompressed bytes
                for i in range(length):
                    if self.inpos >= len(self.packed):
                        break
                    self.unpacked.append(self.packed[self.inpos])
                    self.inpos += 1

            elif command == 1:
                # 8-bit RLE
                if self.inpos >= len(self.packed):
                    break
                value = self.packed[self.inpos]
                self.inpos += 1
                for i in range(length):
                    self.unpacked.append(value)

            elif command == 2:
                # 16-bit RLE
                if self.inpos + 1 >= len(self.packed):
                    break
                value1 = self.packed[self.inpos]
                value2 = self.packed[self.inpos + 1]
                self.inpos += 2
                for i in range(length):
                    self.unpacked.append(value1)
                    self.unpacked.append(value2)

            elif command == 3:
                # 8-bit increasing sequence
                if self.inpos >= len(self.packed):
                    break
                value = self.packed[self.inpos]
                self.inpos += 1
                for i in range(length):
                    self.unpacked.append((value + i) & 0xFF)

            elif command == 4 or command == 7:
                # Regular backref (command 7 behaves same as 4)
                if self.inpos + 1 >= len(self.packed):
                    break
                offset = (self.packed[self.inpos] << 8) | self.packed[self.inpos + 1]
                self.inpos += 2

                if offset + length > len(self.unpacked):
                    # Prevent reading beyond current output
                    for i in range(length):
                        if offset + i < len(self.unpacked):
                            self.unpacked.append(self.unpacked[offset + i])
                else:
                    for i in range(length):
                        self.unpacked.append(self.unpacked[offset + i])

            elif command == 5:
                # Backref with bit rotation
                if self.inpos + 1 >= len(self.packed):
                    break
                offset = (self.packed[self.inpos] << 8) | self.packed[self.inpos + 1]
                self.inpos += 2

                for i in range(length):
                    if offset + i < len(self.unpacked):
                        self.unpacked.append(_rotate(self.unpacked[offset + i]))

            elif command == 6:
                # Backwards backref
                if self.inpos + 1 >= len(self.packed):
                    break
                offset = (self.packed[self.inpos] << 8) | self.packed[self.inpos + 1]
                self.inpos += 2

                for i in range(length):
                    if offset - i >= 0 and offset - i < len(self.unpacked):
                        self.unpacked.append(self.unpacked[offset - i])

        return self.unpacked


class HalCompressor:
    """Compressor for HAL Laboratory format."""

    def __init__(self, data, fast=True):
        self.unpacked = bytearray(data)
        self.inputsize = len(data)
        self.packed = bytearray()
        self.inpos = 0
        self.dontpack = bytearray()
        self.fast = fast

    def compress(self):
        """Compress the data and return result."""
        while self.inpos < self.inputsize:
            # Check for RLE
            rle = self._rle_check()

            # Check for backref (skip if we have a good RLE)
            if rle['size'] < LONG_RUN_SIZE and self.inputsize - self.inpos >= 4:
                backref = self._ref_search()
            else:
                backref = {'size': 0}

            # Use the better compression method
            if backref['size'] > rle['size']:
                self._write_backref(backref)
            elif rle['size'] >= 2:
                self._write_rle(rle)
            else:
                # Write byte as literal
                self._write_next_byte()

        # Flush any remaining literal data
        self._write_raw()

        # Write terminator
        self.packed.append(0xFF)

        return self.packed

    def _rle_check(self):
        """Check for RLE opportunities at current position."""
        current = self.unpacked[self.inpos:]
        best = {'size': 0, 'data': 0, 'method': 0}

        # Check 8-bit RLE
        size = 0
        for i in range(min(LONG_RUN_SIZE, len(current))):
            if current[i] == current[0]:
                size += 1
            else:
                break
        if size > best['size'] and size > 2:
            best = {'size': size, 'data': current[0], 'method': 0}

        # Check 16-bit RLE
        if len(current) >= 2:
            size = 0
            first_word = current[0] | (current[1] << 8)
            for i in range(0, min(2 * LONG_RUN_SIZE, len(current) - 1), 2):
                if i + 1 < len(current):
                    word = current[i] | (current[i + 1] << 8)
                    if word == first_word:
                        size += 2
                    else:
                        break
            if size > best['size'] and size > 2:
                best = {'size': size, 'data': first_word, 'method': 1}

        # Check sequence RLE (skip in fast mode)
        if not self.fast:
            size = 0
            for i in range(min(LONG_RUN_SIZE, len(current))):
                if current[i] == (current[0] + i) & 0xFF:
                    size += 1
                else:
                    break
            if size > best['size'] and size > 2:
                best = {'size': size, 'data': current[0], 'method': 2}

        return best

    def _ref_search(self):
        """Search for back references."""
        current = self.unpacked[self.inpos:]
        best = {'size': 0, 'offset': 0, 'method': 0}

        # Forward reference search
        if len(current) >= 4:
            search_pattern = bytes(current[:4])
            # Search in previously compressed data
            for offset in range(max(0, self.inpos - 8192), self.inpos):
                if self.unpacked[offset:offset+4] == search_pattern:
                    # Found a match, see how long it is
                    size = 4
                    while size < min(LONG_RUN_SIZE, len(current)) and \
                          offset + size < self.inpos and \
                          self.unpacked[offset + size] == current[size]:
                        size += 1

                    if size >= 4 and size > best['size']:
                        best = {'size': size, 'offset': offset, 'method': 0}

        # Skip other reference types in fast mode
        if self.fast:
            return best

        # Rotated reference search
        if len(current) >= 4:
            search_pattern = bytes([_rotate(b) for b in current[:4]])
            for offset in range(max(0, self.inpos - 8192), self.inpos):
                if bytes([_rotate(self.unpacked[offset + i]) for i in range(4)]) == search_pattern:
                    size = 4
                    while size < min(LONG_RUN_SIZE, len(current)) and \
                          offset + size < self.inpos and \
                          _rotate(self.unpacked[offset + size]) == current[size]:
                        size += 1

                    if size >= 4 and size > best['size']:
                        best = {'size': size, 'offset': offset, 'method': 1}

        # Backward reference search
        if len(current) >= 4:
            search_pattern = bytes(current[3::-1])
            for offset in range(max(3, self.inpos - 8192), self.inpos):
                if offset >= 3 and self.unpacked[offset-3:offset+1][::-1] == search_pattern:
                    size = 4
                    while size < min(LONG_RUN_SIZE, len(current)) and \
                          offset - size >= 0 and \
                          self.unpacked[offset - size] == current[size]:
                        size += 1

                    if size >= 4 and size > best['size']:
                        best = {'size': size, 'offset': offset, 'method': 2}

        return best

    def _write_raw(self):
        """Write buffered literal data."""
        if len(self.dontpack) == 0:
            return

        size = len(self.dontpack) - 1

        if size >= RUN_SIZE:
            # Long command
            self.packed.append(0xE0 | (size >> 8))
            self.packed.append(size & 0xFF)
        else:
            # Regular command
            self.packed.append(size)

        # Write the literal data
        self.packed.extend(self.dontpack)
        self.dontpack = bytearray()

    def _write_backref(self, backref):
        """Write a back reference."""
        # Flush literal buffer first
        self._write_raw()

        size = backref['size'] - 1
        method = backref['method']

        if size >= RUN_SIZE:
            # Long command
            self.packed.append((0xF0 + (method << 2)) | (size >> 8))
            self.packed.append(size & 0xFF)
        else:
            # Regular command
            self.packed.append((0x80 + (method << 5)) | size)

        # Write offset (big-endian)
        self.packed.append(backref['offset'] >> 8)
        self.packed.append(backref['offset'] & 0xFF)

        self.inpos += backref['size']

    def _write_rle(self, rle):
        """Write RLE data."""
        # Flush literal buffer first
        self._write_raw()

        method = rle['method']

        if method == 1:  # 16-bit RLE
            size = (rle['size'] // 2) - 1
        else:
            size = rle['size'] - 1

        if size >= RUN_SIZE:
            # Long command
            self.packed.append((0xE4 + (method << 2)) | (size >> 8))
            self.packed.append(size & 0xFF)
        else:
            # Regular command
            self.packed.append((0x20 + (method << 5)) | size)

        # Write the data value
        self.packed.append(rle['data'] & 0xFF)

        # 16-bit RLE needs upper byte too
        if method == 1:
            self.packed.append((rle['data'] >> 8) & 0xFF)

        self.inpos += rle['size']

    def _write_next_byte(self):
        """Buffer a literal byte."""
        self.dontpack.append(self.unpacked[self.inpos])
        self.inpos += 1

        # Flush if buffer is full
        if len(self.dontpack) >= LONG_RUN_SIZE:
            self._write_raw()
