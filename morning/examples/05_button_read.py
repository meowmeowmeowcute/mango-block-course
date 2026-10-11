"""
05 讀取按鈕
==================================================================
觀念：腳位設成「輸入」，用 .value() 讀出 0 或 1

  key1 = Pin("KEY1", Pin.IN, Pin.PULL_DOWN)
  key1.value()   → 按下 = 1，放開 = 0

  Pin.PULL_DOWN：沒按的時候把腳位拉到 0，數值才會穩定（MANGO X4 的按鍵一定要加）。

動手改改看
  1. 改成讀 KEY2
  2. 按住 Key1 亮紅燈、按住 Key2 亮藍燈、都沒按就關燈
  ★ 這個觀念之後會用在 B4 專題的 TODO 2！
"""
import time

import neopixel
from machine import Pin

np = neopixel.NeoPixel(Pin("WS2812B"), 6)
key1 = Pin("KEY1", Pin.IN, Pin.PULL_DOWN)

try:
    while True:
        pressed = key1.value()      # 讀按鈕：0 或 1
        print("Key1 =", pressed)

        if pressed == 1:
            np.fill((30, 0, 0))     # 按住 → 全部紅色
        else:
            np.fill((0, 0, 0))      # 放開 → 關燈
        np.write()

        time.sleep(0.1)
finally:
    np.fill((0, 0, 0))
    np.write()
