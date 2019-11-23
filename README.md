# SoundNet
Are you worried about your high speed internet? Then this project comes to your rescue! It's a state of the art implementation that uses sound waves to send 1 bit per second of Ethernet frame. That's right, 1 bit per second!

## Setup
1. Run `script/up` to create a virtual environment `.venv` with the required packages
2. Activate the virtual environment by running `source .venv/bin/activate`


### Arguments:

`receiver.py`

| Argument | Description | Values |
| :---         |     :---      |          :--- |
| --continuous |     Decide if receiver should listen continuously.      |  Choose from {True, False} |

`sender.py`

| Argument | Description | Values |
| :---         |     :---      |          :--- |
| --source         | MAC address of the source | integer  |
| --destination         | MAC address of the destination | integer  |
| --message         | Message to be sent.| string  |


## Usage:
First run the `receiver.py`:

`python3 receiver.py --continuous=True`

Then in other console run `sender.py`:

`python3 sender.py --source=0 --destination=1 --message='hello world'`

Drink your coffe while the huge amount of data is flowing through your air!

## Features:
- encoding message into Ethernet frame
- decoding Ethernet frame into message
- listening to the sounds from microphone, receiving bits and printing the message
- sending encoded message as a sequence of bits via speaker

## Additional configuration
If you want to change the SPEED or waves frequencies for bits you can do it in `constants.py`.

## Credit
SoundNet uses library "pulseaudio" created by Grzegorz Gutowski. The library is available under LGPL license.
