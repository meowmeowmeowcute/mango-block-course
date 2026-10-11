"""Check which servo ids are on the bus, and whether each one is healthy.

Every id from 0 to MAX_ID - 1 is asked for its position (read only, nothing
moves). An id that answers is asked TRIES times and gets one of three results:

    ok        every reply was clean, exactly one servo has this id
    overlap?  some replies were garbled, two servos probably share this id
    unstable  replies came and went, the connector is probably loose

Run this after wiring, and before and after changing an id. Needs servo.py
on the board.
"""
from servo import send

TRIES = 5   # asks per id that answers
MAX_ID = 10 # check ids 0 .. MAX_ID - 1

def classify(r, sid):
    """"ok" for one clean reply, "none" for silence, "bad" for anything else"""
    if not r:
        return "none"

    # one clean position reply is exactly 8 bytes, extra bytes mean a second reply
    if len(r) == 8 and r[:2] == b"\x55\x55" and r[2] == sid and r[4] == 28 \
            and ~sum(r[2:7]) & 0xFF == r[7]:
        return "ok"

    return "bad"

found = []
overlap = []
unstable = []

for _id in range(MAX_ID):
    # quick look: twice silent means nobody has this id
    first = [classify(send(_id, 28), _id) for _ in range(2)]
    if first == ["none", "none"]:
        continue

    # someone answered, ask more times to see if the replies stay clean
    # position (cmd 28) differs between servos, so two of them garble each other
    results = first + [classify(send(_id, 28), _id) for _ in range(TRIES - 2)]
    ok, bad, none = (results.count(k) for k in ("ok", "bad", "none"))

    if bad:
        overlap.append(_id)
        print(f"ID: {_id} overlap? {ok} ok, {bad} garbled, {none} silent")
    elif none:
        unstable.append(_id)
        print(f"ID: {_id} unstable, {ok} ok, {none} silent, check the connector")
    else:
        found.append(_id)
        print(f"ID: {_id} ok")

print(f"found: {found}")
if overlap:
    print(f"overlap: {overlap}, keep one servo on the bus and change its id")
if unstable:
    print(f"unstable: {unstable}")
