"""Talk to Hiwonder bus servos on the MANGO X4 SS1 header.

Upload this file to the board once, then import it:

    from servo import *

    send(sid, cmd, params)  send one raw packet, return the reply bytes
    pos(sid)                read the position, 0-1000 (0-240 degrees)
    move(sid, p, ms)        turn to position p in ms milliseconds
    beep(n)                 beep the buzzer n times, warn before moving

All servos share one wire, each one only answers to its own id (sid).
"""
from machine import UART, Pin, PWM
import time

# SS1 header: GP8 sends, GP9 receives, hiwonder bus servos talk at 115200
uart = UART(1, 115200, tx=Pin(8), rx=Pin(9))

def send(sid, cmd, params=b"", wait=30) -> bytes:
    """send one packet to servo sid, return its raw reply (b"" if none)"""
    # packet: 55 55 | id | len | cmd | params | checksum, len = params + 3
    body = bytes([sid, len(params) + 3, cmd]) + params

    # drop old bytes so we only read this reply
    while uart.any():
        uart.read(64)

    # checksum = inverted low byte of the sum of id, len, cmd and params
    uart.write(b"\x55\x55" + body + bytes([~sum(body) & 0xFF]))

    # give the servo time to answer, then read what arrived
    time.sleep_ms(wait)
    n = uart.any()
    return (uart.read(min(n, 64)) or b"") if n else b""

def pos(sid):
    """return the position 0-1000 of servo sid, or None"""
    r = send(sid, 28)  # cmd 28 = read position

    # a good reply is 8 bytes from the same id with the same cmd
    if len(r) < 8 or r[2] != sid or r[4] != 28:
        return None

    return r[5] | r[6] << 8  # low byte first

def move(sid, p, ms):
    """turn servo sid to position p (0-1000) in ms milliseconds"""
    # cmd 1 = move, params are position and time, each low byte first
    # move gets no reply, so only wait 5 ms
    send(sid, 1, bytes([p & 0xFF, p >> 8, ms & 0xFF, ms >> 8]), 5)

def beep(n=1):
    """beep the buzzer (GP46) n times"""
    bz = PWM(Pin("BUZZER"), freq=2500, duty_u16=0)
    for _ in range(n):
        bz.duty_u16(32768)  # half duty = loudest tone
        time.sleep_ms(150)
        bz.duty_u16(0)
        time.sleep_ms(250)

    bz.deinit()  # release the pin so it stays silent
