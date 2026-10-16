"""Find the servos on the bus, check their ids, and show the state of each one.

Ids 0 to MAX_ID - 1 are asked for their position (read only, nothing moves).
An id that answers is asked TRIES times, its first reply is printed (it starts
with 55 55 {id}) and it gets one of three results:

    ok        every reply was clean, exactly one servo has this id,
              then its voltage (mV), position (0-1000) and temperature (C)
    overlap?  some replies were garbled, two servos probably share this id
    unstable  replies came and went, the connector is probably loose

Run this after wiring, before moving anything, and before and after changing
an id. Needs servo.py on the board.
"""
from servo import send

MAX_ID = 254 # check ids 0 .. MAX_ID - 1
TRIES = 5   # asks per id that answers

def parse(r, sid, cmd):
    """return the params of a clean reply r, or None"""
    # header must be 55 55, then the same id and cmd we asked
    if len(r) < 6 or r[:2] != b"\x55\x55" or r[2] != sid or r[4] != cmd:
        return None

    # r[3] is len, extra bytes after the checksum mean a second reply
    n = r[3]
    if len(r) != n + 3 or ~sum(r[2:n + 2]) & 0xFF != r[n + 2]:
        return None

    return r[5:n + 2]

def ask(sid, cmd):
    """send cmd to servo sid, return the params of a clean reply, or None"""
    return parse(send(sid, cmd), sid, cmd)

def hexs(r):
    """bytes as spaced hex, like 55 55 03 05 1C ..."""
    return " ".join("%02X" % b for b in r)

def u16(d, signed = False):
    """two bytes, low byte first, to a number"""
    v = d[0] | d[1] << 8
    return v - 0x10000 if signed and v & 0x8000 else v

found = []
overlap = []
unstable = []

for sid in range(MAX_ID):
    print("Scanning ID: %3d" % sid, end="\r")

    # quick look: twice silent means nobody has this id
    replies = [send(sid, 28) for _ in range(2)]
    if not any(replies):
        continue

    # someone answered, ask more times to see if the replies stay clean
    # position (cmd 28) differs between servos, so two of them garble each other
    replies += [send(sid, 28) for _ in range(TRIES - 2)]
    clean = [r for r in replies if parse(r, sid, 28)]
    silent = replies.count(b"")
    garbled = len(replies) - len(clean) - silent

    print("found id", sid, "reply", hexs(next(r for r in replies if r)))

    if garbled:
        overlap.append(sid)
        print("  overlap? %d ok, %d garbled, %d silent" % (len(clean), garbled, silent))
    elif silent:
        unstable.append(sid)
        print("  unstable, %d ok, %d silent, check the connector" % (len(clean), silent))
    else:
        found.append(sid)
        vin, temp = ask(sid, 27), ask(sid, 26)
        pos = u16(clean[-1][5:7], True)
        print("  ok  vin %s mV, pos %s, temp %s C" % (vin and u16(vin), pos, temp and temp[0]))

print(" " * 20, end="\r")
print("found:", found)

if overlap:
    print("overlap:", overlap, "keep one servo on the bus and change its id")
if unstable:
    print("unstable:", unstable)
