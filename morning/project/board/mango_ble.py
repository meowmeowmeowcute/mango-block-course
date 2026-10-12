"""
mango_ble.py — 藍牙儀表板工具庫（上傳到板子用）
==================================================================
用法：上傳到板子（在 VS Code 對這個檔案按右鍵 → Upload File to Board），
然後在 dashboard.py 裡：

    import mango_ble
    mango_ble.run(on_led=..., on_brightness=..., ...)

這個工具庫負責所有藍牙的事情。網頁按下按鈕時，它會呼叫你在 dashboard.py 寫的函式：

  網頁上的操作          會呼叫你的函式
  ─────────────────  ─────────────────────────────
  選顏色、點圓點        on_led(index, r, g, b)    index 0~5；255 = 全部
  拖亮度滑桿           on_brightness(value)      value 0~100（拖動時就會一直送，終端機停下來才印）
  按效果按鈕           on_effect(number)         0 靜態 1 彩虹 2 呼吸 3 跑馬燈 4 警示燈
  按琴鍵              tone_on(freq) → 時間到 → tone_off()
  按小遊戲「開始」      on_game_start()

  工具庫也會一直呼叫：
    read_keys()   每 0.01 秒，要回傳 (key1 的值, key2 的值)，網頁上的方塊會跟著亮
    tick(frame)   每 0.03 秒，畫一格彩燈動畫；frame 是第幾格（0, 1, 2, …）

  你也可以呼叫工具庫：
    mango_ble.game_result(ms)   把小遊戲的結果傳給網頁（毫秒；-1 代表偷跑）
    mango_ble.beep(freq, ms)    嗶一聲（會用你的 tone_on / tone_off），不用自己 sleep

你的函式出錯時，工具庫會印出錯誤訊息，但不會中斷藍牙連線。
做 TODO 不需要改這個檔案；想自己加新功能（自由發揮）時，請看下面「怎麼新增一個功能」。

──── 怎麼新增一個功能（例如網頁多一個按鈕）────────────────────────
  板子端（這個檔案）
    1. 在「特徵值」那一段，照著樣子新增一行 Characteristic，取一個新的編號，例如 "3407"
    2. 照著 _on_effect() 的樣子寫一個 _on_xxx()：等網頁寫入 → 呼叫 _call("你的函式名", ...)
    3. 在 _main() 的 tasks 裡加上 _on_xxx
    4. 在 run() 加一個參數，dashboard.py 就能把自己的函式交進來
    （修改後要重新 Upload File to Board）
  網頁端
    5. mango-ble.js 的 MANGO_CHARS 加上同一個編號的 UUID
    6. index.html 加一個按鈕，app.js 寫它的 onclick：await mango.write("xxx", [...])

GATT 協定（和網頁的 mango-ble.js 一致）
  服務 4d414e47-4f58-3400-8000-000000000000
  led 3401 (read/write [index,R,G,B])、brightness 3402 (read/write 1 byte)、
  effect 3403 (read/write 1 byte)、buzzer 3404 (write <HH 頻率,毫秒)、
  keys 3405 (read/notify bit0=Key1 bit1=Key2)、game 3406 (write 1=開始；notify <h 毫秒，-1=偷跑)
"""
import asyncio
import struct
import sys

import aioble
import bluetooth


def _uuid(mid):
    return bluetooth.UUID("4d414e47-4f58-%s-8000-000000000000" % mid)


_SERVICE_UUID = _uuid("3400")

# ---- 特徵值：網頁和板子交換資料的「信箱」，每個都有自己的編號 ----
_service = aioble.Service(_SERVICE_UUID)
_led_char = aioble.Characteristic(_service, _uuid("3401"), read=True, write=True, capture=True)
# 亮度：拖滑桿會連續送很多筆，所以「不用回覆」(write_no_response)、也不排隊 (capture=False)，只取最新的值
_bright_char = aioble.Characteristic(_service, _uuid("3402"), read=True, write=True, write_no_response=True)
_effect_char = aioble.Characteristic(_service, _uuid("3403"), read=True, write=True, capture=True)
_buzzer_char = aioble.Characteristic(_service, _uuid("3404"), write=True, capture=True)
_keys_char = aioble.Characteristic(_service, _uuid("3405"), read=True, notify=True)
_game_char = aioble.Characteristic(_service, _uuid("3406"), read=True, write=True, notify=True, capture=True)
aioble.register_services(_service)

_colors = bytearray(18)  # 網頁連線時讀回目前顏色用
_cb = {}
_last_error = {}


def _nothing(*args):
    return None


def _call(name, *args):
    """呼叫學生的函式；出錯時印出訊息（同樣的錯誤只印一次），不讓藍牙斷掉。"""
    try:
        result = _cb[name](*args)
        _last_error.pop(name, None)
        return result
    except Exception as e:
        msg = repr(e)
        if _last_error.get(name) != msg:
            _last_error[name] = msg
            print("\n⚠ 你的", name, "出錯了：")
            sys.print_exception(e)
        return None


# ---------------------------------------------------------------------
# 網頁寫入 → 呼叫學生的函式
# ---------------------------------------------------------------------
async def _on_led():
    while True:
        _, data = await _led_char.written()
        if len(data) != 4:
            print("[led] 需要 4 bytes，收到", len(data))
            continue
        index, r, g, b = data
        if index == 255:
            for i in range(6):
                _colors[i * 3:i * 3 + 3] = bytes((r, g, b))
        elif index < 6:
            _colors[index * 3:index * 3 + 3] = bytes((r, g, b))
        else:
            print("[led] index 超出範圍：", index)
            continue
        _led_char.write(bytes(_colors))
        print("[網頁] on_led(%d, %d, %d, %d)" % (index, r, g, b))
        _call("on_led", index, r, g, b)


async def _on_brightness():
    pending = None  # 還沒印到終端機的值：拖動時不一直 print（print 很慢，會拖慢藍牙），停下來 0.3 秒才印
    while True:
        try:
            await _bright_char.written(timeout_ms=300 if pending is not None else None)
        except asyncio.TimeoutError:
            print("[網頁] on_brightness(%d)" % pending)
            pending = None
            continue
        data = _bright_char.read()   # 只拿最新的值，中間的直接跳過
        if len(data) != 1:
            continue
        value = min(data[0], 100)
        _call("on_brightness", value)
        pending = value


async def _on_effect():
    while True:
        _, data = await _effect_char.written()
        if len(data) != 1 or data[0] > 4:
            print("[effect] 無效：", bytes(data))
            continue
        _effect_char.write(bytes(data))
        print("[網頁] on_effect(%d)" % data[0])
        _call("on_effect", data[0])


async def _on_game():
    while True:
        _, data = await _game_char.written()
        if len(data) != 1 or data[0] != 1:
            continue
        print("[網頁] on_game_start()")
        _call("on_game_start")


def game_result(ms):
    """把小遊戲的結果傳給網頁：反應時間（毫秒），-1 代表偷跑。dashboard.py 會呼叫這個函式。"""
    ms = max(-1, min(int(ms), 32767))
    print("[板子] game_result(%d)" % ms)
    _game_char.write(struct.pack("<h", ms), send_update=True)


_tone_task = None


async def _tone(freq, ms):
    try:
        _call("tone_on", freq)
        await asyncio.sleep_ms(ms)
    finally:
        _call("tone_off")


def _play(freq, ms):
    global _tone_task
    if _tone_task is not None:
        _tone_task.cancel()
        _tone_task = None
    _call("tone_off")
    if freq > 0 and ms > 0:
        _tone_task = asyncio.create_task(_tone(max(50, min(freq, 8000)), min(ms, 3000)))


def beep(freq, ms):
    """嗶一聲：呼叫你的 tone_on(freq)，ms 毫秒後呼叫 tone_off()。不會卡住程式。"""
    _play(freq, ms)


async def _on_buzzer():
    while True:
        _, data = await _buzzer_char.written()
        if len(data) != 4:
            print("[buzzer] 需要 4 bytes，收到", len(data))
            continue
        freq, ms = struct.unpack("<HH", data)
        print("[網頁] tone_on(%d)，%d 毫秒後 tone_off()" % (freq, ms))
        _play(freq, ms)


# ---------------------------------------------------------------------
# 背景工作
# ---------------------------------------------------------------------
async def _tick_task():
    frame = 0
    while True:
        _call("tick", frame)
        frame += 1
        await asyncio.sleep_ms(30)


def _read_mask():
    keys = _call("read_keys")
    if not keys:
        return 0
    return (1 if keys[0] else 0) | (2 if keys[1] else 0)


async def _keys_task():
    last = -1
    while True:
        mask = _read_mask()
        if mask != last:
            await asyncio.sleep_ms(20)  # 去彈跳：20 ms 後再確認一次
            if _read_mask() == mask:
                last = mask
                _keys_char.write(bytes([mask]), send_update=True)
        await asyncio.sleep_ms(10)


async def _peripheral(name):
    while True:
        print("📡 等待網頁連線…  我的名字是：", name)
        connection = await aioble.advertise(250_000, name=name, services=[_SERVICE_UUID])
        print("✅ 已連線")
        _play(1320, 120)
        await connection.disconnected(timeout_ms=None)
        print("✗ 已斷線")
        _play(440, 120)


async def _main():
    ble = bluetooth.BLE()
    _, mac = ble.config("mac")
    name = "MANGO-%02X%02X" % (mac[-2], mac[-1])
    ble.config(gap_name=name)
    # 每個網頁功能一個背景工作；新增功能時，把你的 _on_xxx 加在這裡
    for task in (_on_led, _on_brightness, _on_effect, _on_buzzer, _on_game, _tick_task, _keys_task):
        asyncio.create_task(task())
    await _peripheral(name)


def run(on_led=None, on_brightness=None, on_effect=None, tone_on=None, tone_off=None,
        read_keys=None, tick=None, on_game_start=None):
    """啟動藍牙儀表板。這個函式不會結束，要按 Stop 才會停。"""
    _cb.update(
        on_led=on_led or _nothing,
        on_brightness=on_brightness or _nothing,
        on_effect=on_effect or _nothing,
        tone_on=tone_on or _nothing,
        tone_off=tone_off or _nothing,
        read_keys=read_keys or _nothing,
        tick=tick or _nothing,
        on_game_start=on_game_start or _nothing,
    )
    _bright_char.write(bytes([30]))
    _effect_char.write(bytes([0]))
    _led_char.write(bytes(_colors))
    _keys_char.write(bytes([0]))
    _game_char.write(struct.pack("<h", 0))
    try:
        asyncio.run(_main())
    finally:
        asyncio.new_event_loop()
