import time

from servo import *

SERVO_COUNT = 3  # servos with ids 1 .. SERVO_COUNT
OFFSET = 50      # how far to turn, 1000 = 240 degrees, so 50 is about 12 degrees
MOVE_MS = 1000   # how long one move takes, in milliseconds

for sid in range(1, SERVO_COUNT + 1):
    home = pos(sid)
    if home is None:
        print("id", sid, "did not answer, skip it")
        continue

    beep(sid)  # beeps = id, hands off before it moves
    print("id", sid, "starts at", home)

    # turn toward the middle so it never hits the end of its range
    target = home + OFFSET if home < 500 else home - OFFSET
    move(sid, target, MOVE_MS)
    time.sleep_ms(MOVE_MS + 200)  # wait for the move, plus a little extra
    print("  went to", pos(sid))

    move(sid, home, MOVE_MS)
    time.sleep_ms(MOVE_MS + 200)
    print("  back at", pos(sid))
