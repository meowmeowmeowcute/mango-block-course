"""
03 讀取按鈕：按住才亮、按一下切換
==================================================================
觀念 1：腳位設成「輸入」，用 .value() 讀出 0 或 1

  key1 = Pin("KEY1", Pin.IN, Pin.PULL_DOWN)
  key1.value()   → 按下 = 1，放開 = 0

  Pin.PULL_DOWN：沒按的時候把腳位拉到 0，數值才會穩定（板子上的按鍵一定要加）。

觀念 2：偵測「按下的那一瞬間」
  按住才亮：只看「現在」是 0 還是 1                     ← Key1
  按一下切換：抓數值從 0 變成 1 的那一刻                 ← Key2
      上一次 = 0、這一次 = 1  → 剛剛被按下

  為什麼每次要等 0.02 秒？按鈕裡的金屬片接觸時會彈跳，0 和 1 會快速跳好幾次，
  不等一下的話，按一次可能會被當成按好幾次（稱為「去彈跳」）。

動手改改看
  1. 按住 Key1 改成亮藍燈
  2. 把 time.sleep(0.02) 改成 0，快速按 Key2 幾次，看看會不會亂跳
  3. 每按一次 Key2 換一個顏色：紅 → 綠 → 藍 → 紅 …（提示：用一個串列存顏色）
  ★ 讀按鈕會用在網頁儀表板實作的 TODO 2；「剛剛被按下」會用在 TODO 7（反應力小遊戲）！
"""
import time

import neopixel
from machine import Pin

np = neopixel.NeoPixel(Pin("WS2812B"), 6)
key1 = Pin("KEY1", Pin.IN, Pin.PULL_DOWN)
key2 = Pin("KEY2", Pin.IN, Pin.PULL_DOWN)

light_on = False    # Key2 切換的燈現在是開還是關
last2 = 0           # 上一次讀到的 Key2

try:
    while True:
        now1 = key1.value()                 # 讀按鈕：0 或 1
        now2 = key2.value()

        # --- 觀念 2-2：Key2 從 0 變成 1 → 剛剛被按下，開 ↔ 關 互換 ---
        if last2 == 0 and now2 == 1:
            light_on = not light_on
            print("Key2 切換！燈現在是", "開" if light_on else "關")
        last2 = now2

        # --- 觀念 2-1：Key1 按住才亮（優先）；其他時候照 Key2 的開關 ---
        if now1 == 1:
            np.fill((30, 0, 0))             # 按住 Key1 → 全部紅色
        elif light_on:
            np.fill((30, 30, 30))           # Key2 開 → 白色
        else:
            np.fill((0, 0, 0))              # 關燈
        np.write()

        time.sleep(0.02)                    # 去彈跳
finally:
    np.fill((0, 0, 0))
    np.write()
