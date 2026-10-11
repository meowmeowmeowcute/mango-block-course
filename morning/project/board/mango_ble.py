"""
mango_ble.py — 藍牙儀表板工具庫（已完成，學生不需要看懂、也不要修改）
==================================================================
用法：上傳到板子（在 VS Code 對這個檔案按右鍵 → Upload File to Board），
然後在 dashboard.py 裡：

    import mango_ble
    mango_ble.run(on_led=..., on_brightness=..., ...)

這個工具庫負責所有藍牙的事情。網頁按下按鈕時，它會呼叫你在 dashboard.py 寫的函式：

  網頁上的操作          會呼叫你的函式
  ─────────────────  ─────────────────────────────
  選顏色、點圓點        on_led(index, r, g, b)    index 0~5；255 = 全部
  拖亮度滑桿           on_brightness(value)      value 0~100
  按效果按鈕           on_effect(number)         0 靜態 1 彩虹 2 呼吸 3 跑馬燈 4 警示燈
  按琴鍵              tone_on(freq) → 時間到 → tone_off()

  工具庫也會一直呼叫：
    read_keys()   每 0.01 秒，要回傳 (key1 的值, key2 的值)，網頁上的方塊會跟著亮
    tick(frame)   每 0.03 秒，畫一格彩燈動畫；frame 是第幾格（0, 1, 2, …）

  晶片溫度由工具庫自己讀取、傳給網頁。

你的函式出錯時，工具庫會印出錯誤訊息，但不會中斷藍牙連線。

GATT 協定（給老師參考，和網頁的 mango-ble.js 一致）
  服務 4d414e47-4f58-3400-8000-000000000000
  led 3401 (read/write [index,R,G,B])、brightness 3402 (read/write 1 byte)、
  effect 3403 (read/write 1 byte)、buzzer 3404 (write <HH 頻率,毫秒)、
  keys 3405 (read/notify bit0=Key1 bit1=Key2)、temp 3406 (read/notify <h °C×100)
"""
import asyncio
import struct
import sys

import aioble
import bluetooth
from machine import ADC


def _uuid(mid):
    return bluetooth.UUID("4d414e47-4f58-%s-8000-000000000000" % mid)


_SERVICE_UUID = _uuid("3400")

_service = aioble.Service(_SERVICE_UUID)
_led_char = aioble.Characteristic(_service, _uuid("3401"), read=True, write=True, capture=True)
_bright_char = aioble.Characteristic(_service, _uuid("3402"), read=True, write=True, capture=True)
_effect_char = aioble.Characteristic(_service, _uuid("3403"), read=True, write=True, capture=True)
_buzzer_char = aioble.Characteristic(_service, _uuid("3404"), write=True, capture=True)
_keys_char = aioble.Characteristic(_service, _uuid("3405"), read=True, notify=True)
_temp_char = aioble.Characteristic(_service, _uuid("3406"), read=True, notify=True)
aioble.register_services(_service)

_temp_adc = ADC(ADC.CORE_TEMP)
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


def _core_temp():
    total = 0
    for _ in range(16):
        total += _temp_adc.read_u16()
    v = total / 16 * 3.3 / 65535
    return 27 - (v - 0.706) / 0.001721


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
    while True:
        _, data = await _bright_char.written()
        if len(data) != 1:
            continue
        value = min(data[0], 100)
        _bright_char.write(bytes([value]))
        print("[網頁] on_brightness(%d)" % value)
        _call("on_brightness", value)


async def _on_effect():
    while True:
        _, data = await _effect_char.written()
        if len(data) != 1 or data[0] > 4:
            print("[effect] 無效：", bytes(data))
            continue
        _effect_char.write(bytes(data))
        print("[網頁] on_effect(%d)" % data[0])
        _call("on_effect", data[0])


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


async def _temp_task():
    while True:
        _temp_char.write(struct.pack("<h", int(_core_temp() * 100)), send_update=True)
        await asyncio.sleep_ms(1000)


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
    for task in (_on_led, _on_brightness, _on_effect, _on_buzzer, _tick_task, _keys_task, _temp_task):
        asyncio.create_task(task())
    await _peripheral(name)


def run(on_led=None, on_brightness=None, on_effect=None, tone_on=None, tone_off=None,
        read_keys=None, tick=None):
    """啟動藍牙儀表板。這個函式不會結束，要按 Stop 才會停。"""
    _cb.update(
        on_led=on_led or _nothing,
        on_brightness=on_brightness or _nothing,
        on_effect=on_effect or _nothing,
        tone_on=tone_on or _nothing,
        tone_off=tone_off or _nothing,
        read_keys=read_keys or _nothing,
        tick=tick or _nothing,
    )
    _bright_char.write(bytes([30]))
    _effect_char.write(bytes([0]))
    _led_char.write(bytes(_colors))
    _keys_char.write(bytes([0]))
    _temp_char.write(struct.pack("<h", 0))
    try:
        asyncio.run(_main())
    finally:
        asyncio.new_event_loop()
