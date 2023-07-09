## XBee MicroPython
### [MicroPython](https://micropython.org/) code to control [Digi XBee](https://www.digi.com/products/embedded-systems/digi-xbee/rf-modules/2-4-ghz-rf-modules/xbee-zigbee) Series 2C devices with a microcontroller.

Digi's newer XBee3 already has MicroPython and I've found it to be a great little microcontroller. One use is monitoring my laundy: [xbee3-laundry](https://github.com/idatum/xbee3-laundry). However, I still have a couple XBee Series 2C devices around that I like to interface with various microcontrollers. I recently spent a Saturday giving micropython a try on my [Raspberry Pi Pico](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html) and couldn't find an existing XBee API implementation. **xbee-mpy** is my own implementation based on Digi's documentation of their ZigBee API. I did something similar for C# with [xbeesharp](https://github.com/idatum/xbeesharp).

**xbee-mpy** allows my Pico to transmit data as well as receive messages over an XBee ZigBee mesh network. Specifically, this implementation handles transmit and receive packets, both escaped and unescaped. Any other microcontroller running MicroPython with a UART should be able to use this code with an Xbee.

Here is a simple example that waits to receive a "blink" message to toggle the Pico LED and transmits an acknowledge back:
```
from time import sleep
from machine import Pin
from machine import UART
from xbee_serial import XbeeSerial
import xbee_frame
import xbee_frame_builder as builder

led = Pin("LED", Pin.OUT)
xbs = XbeeSerial(UART(0, baudrate=115200), escaped=True)
rx_frame = xbs.receive()
if rx_frame.get_rame_type() == xbee_frame.FRAME_TYPE_RECEIVE:
    src_addr = rx_frame.get_source_address()
    msg = rx_frame.get_receive_data().decode()
    if msg == "blink":
        led.toggle()
        sleep(.5)
        led.toggle()
        tx_frame = builder.create_transmit_frame(address=src_addr,
                                                 frame_id=1,
                                                 tx_data="ACK blink".encode(),
                                                 escaped=True)
        xbs.transmit(tx_frame)
```

It can use some optimization around allocating the bytes, maybe pre-allocating a bytearray once the packet length field is received.