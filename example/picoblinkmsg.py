"""Example for Raspberry Pi Pico with XBee S2C connected to UART0."""
from time import sleep
from machine import Pin
from machine import UART
from xbee_serial import XbeeSerial
import xbee_frame
import xbee_frame_builder as builder

led = Pin("LED", Pin.OUT)
xbs = XbeeSerial(UART(0, baudrate=115200), True)
rx_frame = xbs.receive()
if rx_frame.get_frame_type() == xbee_frame.FRAME_TYPE_RECEIVE:
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
