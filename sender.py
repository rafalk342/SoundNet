import argparse

import numpy as np
import math

import pulseaudio as pa
from ethernet_frame import Encoder
from constants import *


def get_tone_sin(frequency, time):
    return [math.sin(2 * PI * x * frequency / FRAMERATE) for x in
            range(int(time * FRAMERATE))]


def parse_args():
    """
    Parse arguments from command line input
    """
    parser = argparse.ArgumentParser(description='Sender parameters')
    parser.add_argument('--source', type=int, default='0',
                        help='MAC address of the source', )
    parser.add_argument('--destination', type=int, default='1',
                        help='MAC address of the destination', )
    parser.add_argument('--message', type=str, default='hello world',
                        help='Message to be sent.', )
    args, unknown = parser.parse_known_args()
    return args


def main():
    # Parse arguments
    args = parse_args()
    print(f'I am sending message {args.message} to {args.destination} from '
          f'{args.source}.')

    with pa.simple.open(direction=pa.STREAM_PLAYBACK, format=pa.SAMPLE_S16LE,
                        rate=FRAMERATE, channels=1) as player:
        bits = Encoder.encode(args.source, args.destination, args.message)
        print(f'Encoded bits {bits}')
        for bit in bits:
            freq = FREQS[bit]
            tone = get_tone_sin(freq, BIT_PER_SECOND)
            player.write(np.array(tone) * (2 ** 15) * AMPLITUDE)
        player.drain()


if __name__ == '__main__':
    main()
