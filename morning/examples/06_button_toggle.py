"""
06 按一下開、再按一下關
==================================================================
觀念：偵測「按下的那一瞬間」

  05 是「按住才亮」。如果要「按一下切換」，要抓的是數值從 0 變成 1 的那一刻：
      上一次 = 0、這一次 = 1  → 剛剛被按下

  為什麼要等 0.02 秒？按鈕裡的金屬片接觸時會彈跳，0 和 1 會快速跳好幾次，
  不等一下的話，按一次可能會被當成按好幾次（稱為「去彈跳」）。

動手改改看
  1. 把 time.sleep(0.02) 刪掉，快速按幾次，看看會不會亂跳
  2. 每按一次 Key1 換一個顏色：紅 → 綠 → 藍 → 紅 …（提示：用一個串列存顏色）
"""
import time

import neopixel
from machine import Pin

np = neopixel.NeoPixel(Pin("WS2812B"), 6)
key1 = Pin("KEY1", Pin.IN, Pin.PULL_DOWN)

light_on = False    # 燈現在是開還是關
last = 0            # 上一次讀到的按鈕數值

try:
    while True:
        now = key1.value()

        if last == 0 and now == 1:          # 從 0 變成 1：剛剛被按下！
            light_on = not light_on         # 開 ↔ 關 互換
            print("切換！燈現在是", "開" if light_on else "關")

            if light_on:
                np.fill((30, 30, 30))
            else:
                np.fill((0, 0, 0))
            np.write()

        last = now
        time.sleep(0.02)                    # 去彈跳
finally:
    np.fill((0, 0, 0))
    np.write()
