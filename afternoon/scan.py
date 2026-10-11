"""Find the servos on the bus and show the state of each one.

Ids 0 to MAX_ID - 1 are asked for their voltage once (read only, nothing moves). Every
id that answers is then read again for:

    vin   supply voltage in mV, about 12000 on a 12 V supply
    pos   position 0-1000 (0-240 degrees)
    temp  temperature in degrees C

Each id is asked only once, so two servos sharing an id give a garbled reply
and that id is simply missing from the list. If an id you expect is missing,
run check_id.py. Needs servo.py on the board.
"""
from servo import send

MAX_ID = 10 # check ids 0 .. MAX_ID - 1

def parse(r, sid, cmd):
    """return the params of a clean reply r, or None"""
    if len(r) < 6 or r[:2] != b"\x55\x55" or r[2] != sid or r[4] != cmd:
        return None

    n = r[3]
    if len(r) < n + 3 or ~sum(r[2:n + 2]) & 0xFF != r[n + 2]:
        return None  # garbled, e.g. two servos share this id

    return r[5:n + 2]

def ask(sid, cmd):
    """send cmd to servo sid, return the params of a clean reply, or None"""
    return parse(send(sid, cmd), sid, cmd)

def hexs(r):
    """bytes as spaced hex, like 55 55 03 05 1B ..."""
    return " ".join("%02X" % b for b in r)

def u16(d, signed = False):
    v = d[0] | d[1] << 8
    return v - 0x10000 if signed and v & 0x8000 else v

found = []
for sid in range(MAX_ID):
    r = send(sid, 27)
    if parse(r, sid, 27):
        found.append(sid)
        print("found id", sid, "reply", hexs(r))  # starts with 55 55 {id}

print("ids", found)

for sid in found:
    vin, pos, temp = ask(sid, 27), ask(sid, 28), ask(sid, 26)
    print("id %d: vin %s mV, pos %s, temp %s C" % (
        sid,
        vin and u16(vin),
        pos and u16(pos, True),
        temp and temp[0],
    ))