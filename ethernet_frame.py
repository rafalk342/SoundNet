import binascii


def get_bytes(bits):
    """Returns bytes from list of bits"""
    number = int(''.join(bits), 2)
    return number.to_bytes(len(bits) // 8, byteorder='big')


def get_bits(byte_size, number):
    """Returns last byte_size*8 bits from number."""
    res = []
    for i in range(byte_size * 8):
        res.append(str(number % 2))
        number //= 2
    res.reverse()
    return res


def get_hash(data):
    """Returns 4 bytes of hash for data."""
    return binascii.crc32(get_bytes(data)) & 0xffffffff


class Encoder:
    """A class for encoding destination, source, and payload into encoded bits."""

    encoding_table = {
        '0000': '11110',
        '0001': '01001',
        '0010': '10100',
        '0011': '10101',
        '0100': '01010',
        '0101': '01011',
        '0110': '01110',
        '0111': '01111',
        '1000': '10010',
        '1001': '10011',
        '1010': '10110',
        '1011': '10111',
        '1100': '11010',
        '1101': '11011',
        '1110': '11100',
        '1111': '11101',
    }

    def __init__(self, source, destination, payload):
        self.source = get_bits(6, source)
        self.destination = get_bits(6, destination)
        self.length = get_bits(2, len(payload))
        self.payload = self.convert_to_bits(payload)
        self.data = self.destination + self.source + self.length + self.payload
        self.hash = get_bits(4, get_hash(self.data))

        self.preamble = self.get_preamble()
        self.frame_delimiter = self.get_frame_delimiter()
        self.frame = self.preamble + self.frame_delimiter + self.four_to_five(
            self.data + self.hash)

    @staticmethod
    def encode(source, destination, message):
        """Returns encoded frame with preamble, destination, source, message, hash as a string of bits."""
        frame = Encoder(source, destination, message)
        return ''.join(frame.frame)

    def convert_to_bits(self, payload):
        """Converts bytes to bits."""
        res = []
        for byte in payload:
            res += get_bits(1, ord(byte))
        return res

    def get_alternating_binary(self, size):
        """Returns list with alternating 1 and 0."""
        res = []
        cur = 1
        for i in range(size):
            res.append(str(cur))
            cur = (cur + 1) % 2
        return res

    def get_preamble(self):
        """Returns ethernet preamble."""
        return self.get_alternating_binary(7 * 8)

    def get_frame_delimiter(self):
        """Returns preamble delimiter."""
        res = self.get_alternating_binary(6)
        res += ['1', '1']
        return res

    def four_to_five(self, bits):
        """Converts bits to 4/5b coding."""
        res = ''
        for i in range(0, len(bits), 4):
            tmp = bits[i:i + 4]
            res = res + self.encoding_table[''.join(tmp)]
        return list(res)


class Decoder:
    """"A class for decoding bits into destination, source and payload."""

    decoding_table = {
        '11110': '0000',
        '01001': '0001',
        '10100': '0010',
        '10101': '0011',
        '01010': '0100',
        '01011': '0101',
        '01110': '0110',
        '01111': '0111',
        '10010': '1000',
        '10011': '1001',
        '10110': '1010',
        '10111': '1011',
        '11010': '1100',
        '11011': '1101',
        '11100': '1110',
        '11101': '1111', }

    def __init__(self, message, with_preamble):
        if with_preamble:
            message = message[8 * 8:]

        self.data = []
        message = self.five_to_four(message)

        self.destination = self.get_destination(message)
        self.data += message[:6 * 8]
        message = message[6 * 8:]

        self.source = self.get_source(message)
        self.data += message[:6 * 8]
        message = message[6 * 8:]

        self.length = self.get_length(message)
        self.data += message[:2 * 8]
        message = message[2 * 8:]

        self.payload = self.get_message(self.length, message)
        self.data += message[:self.length * 8]
        message = message[self.length * 8:]

        self.hash = message
        self.check_hash()

    @staticmethod
    def decode(text, with_preamble=True):
        """Returns source, destination, payload from string of bits."""
        try:
            decoder = Decoder(text, with_preamble)
            return ' '.join((str(decoder.source), str(decoder.destination),
                             decoder.payload))
        except:
            return "Not valid message."

    def get_destination(self, message):
        """Returns destination from message."""
        text = message[0: 6 * 8]
        return int(text, 2)

    def get_source(self, message):
        """Returns source from message."""
        text = message[0:6 * 8]
        return int(text, 2)

    def get_length(self, message):
        """Returns length of the message."""
        text = message[0:2 * 8]
        return int(text, 2)

    def get_message(self, length, message):
        """Returns length message."""
        text = get_bytes(message[0:length * 8])
        return text.decode()

    def five_to_four(self, message):
        """Decodes bits from 4/5b coding."""
        res = ''
        for i in range(0, len(message), 5):
            tmp = message[i:i + 5]
            res = res + self.decoding_table[tmp]
        return ''.join(res)

    def check_hash(self):
        data_hash = ''.join(get_bits(4, get_hash(self.data)))
        if data_hash != self.hash:
            raise Exception("Wrong hash")
