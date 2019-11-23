import argparse

import numpy as np
import pulseaudio as pa
from ethernet_frame import Decoder
from constants import *


class Receiver:
    """
    A class for listening to the message
    """

    def __init__(self, player):
        self.player = player
        self.synced = False
        self.bits = []
        self.preamble_ended = False
        self.preamble_started = False

    def listen(self):
        while True:
            values, fft_value, hertz = self.get_hertz(self.player)
            if self.in_range(hertz):
                self.handle_syncing_player(fft_value, hertz, values)

                self.handle_preamble()

                self.bits.append(self.hertz_to_bit(hertz))

                print(''.join(self.bits))
            elif len(self.bits):
                print(Decoder.decode(''.join(self.bits), with_preamble=False))
                return

    def handle_syncing_player(self, fft_value, hertz, values):
        if not self.synced and self.hertz_to_bit(hertz) == '1':
            self.sync_player(values, fft_value)
            self.synced = True

    def handle_preamble(self):
        if not self.preamble_started:
            print("Preamble started.")
            self.preamble_started = True
        elif not self.preamble_ended and len(self.bits) > 10 and \
                self.bits[
                    -1] == '1' and self.bits[-2] == '1':
            print("Preamble ended.")
            self.preamble_ended = True
            self.bits = []

    def get_hertz(self, player):
        """Returns read values, fft max value and calculated hertz from player."""
        values = player.read(int(FRAMERATE * BIT_PER_SECOND))
        fft_array = np.fft.fft(values)
        freqs = np.fft.fftfreq(len(fft_array))

        sorted_indicies = np.argsort(np.abs(fft_array))
        idx = sorted_indicies[-1]

        freq = freqs[idx]
        freq_in_hertz = abs(freq * FRAMERATE)

        hertz = int(freq_in_hertz)
        fft_value = abs(fft_array[idx])

        return values, fft_value, hertz

    def sync_player(self, values, fft_value):
        """Syncing player with the source clock."""
        while True:
            new_start = int(FRAMERATE * BIT_PER_SECOND * 0.1)
            values = np.concatenate([values[new_start:], self.player.read(
                int(FRAMERATE * BIT_PER_SECOND * 0.1))])
            fft_array = np.fft.fft(values)
            sorted_indicies = np.argsort(np.abs(fft_array))
            idx = sorted_indicies[-1]
            current_value = abs(fft_array[idx])
            if current_value < fft_value:
                break
            fft_value = current_value

    def in_range(self, hertz):
        if FREQ_ZERO - ACCEPTED_MARGIN <= hertz <= FREQ_ZERO + ACCEPTED_MARGIN:
            return True
        if FREQ_ONE - ACCEPTED_MARGIN <= hertz <= FREQ_ONE + ACCEPTED_MARGIN:
            return True
        return False

    def hertz_to_bit(self, hertz):
        if FREQ_ZERO - ACCEPTED_MARGIN <= hertz <= FREQ_ZERO + ACCEPTED_MARGIN:
            return '0'
        else:
            return '1'


def parse_args():
    """
    Parse arguments from command line input
    """
    parser = argparse.ArgumentParser(description='Receiver parameters')
    parser.add_argument('--continuous', type=bool, default=True,
                        help='Decide if receiver should listen continuously.',
                        choices=[True, False])
    args, unknown = parser.parse_known_args()
    return args


def main():
    # Parse arguments
    args = parse_args()

    with pa.simple.open(direction=pa.STREAM_RECORD, format=pa.SAMPLE_S16LE,
                        rate=FRAMERATE, channels=1) as player:
        while True:
            Receiver(player).listen()
            if not args.continuous:
                break


if __name__ == '__main__':
    main()
