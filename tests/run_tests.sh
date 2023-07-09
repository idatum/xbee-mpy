#!/bin/sh

cp ../xbee_frame.py ../xbee_frame_builder.py ../xbee_serial.py .

python xbee_frame_test.py
python xbee_serial_test.py