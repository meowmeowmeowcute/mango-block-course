"""
03 讀取按鍵：按住才亮、按一下切換
==================================================================
① 讀按鍵：button1.value() 會得到 1（按下）或 0（放開）

② 按鍵 1 —— 按住才亮：只看「現在」是不是 1

③ 按鍵 2 —— 按一下切換：抓「上一次是 0、這一次是 1」的那一瞬間
                         （= 剛剛被按下），燈就開 ↔ 關 互換

動手改改看
  1. 按住按鍵 1 改成亮藍燈 (0, 0, 30)
  2. 在迴圈裡加一行 print(button2_now)，按一下按鍵 2，終端機印出幾個 1？
  ★ 讀按鍵會用在網頁儀表板實作的 TODO 2；「剛剛被按下」會用在小遊戲挑戰！
"""
import time

import neopixel
from machine import Pin

leds = neopixel.NeoPixel(Pin("WS2812B"), 6)          # 6 顆彩燈

# 按鍵：Pin.IN 代表「讀進來」；Pin.PULL_DOWN 讓沒按的時候固定是 0
#   MANGO BLOCK 板子上已經有下拉電阻，不加也不會出錯；但不是每塊板子都有，養成習慣加上
button1 = Pin("KEY1", Pin.IN, Pin.PULL_DOWN)         # 按鍵 1（Key1）
button2 = Pin("KEY2", Pin.IN, Pin.PULL_DOWN)         # 按鍵 2（Key2）

RED = (30, 0, 0)
WHITE = (30, 30, 30)
OFF = (0, 0, 0)

light_is_on = False     # 按鍵 2 控制的燈，現在是開還是關
button2_before = 0      # 上一次讀到的按鍵 2（用來抓「剛剛被按下」）

try:
    while True:
        button1_now = button1.value()     # 現在的按鍵 1：1 = 按下，0 = 放開
        button2_now = button2.value()     # 現在的按鍵 2

        # ③ 按鍵 2：上一次是 0、這一次是 1 → 剛剛被按下 → 開關互換
        if button2_before == 0 and button2_now == 1:
            light_is_on = not light_is_on
            print("按鍵 2 切換！燈現在是", "開" if light_is_on else "關")
        button2_before = button2_now      # 記住這一次，下一圈拿來比

        # ② 按鍵 1：按住就亮紅燈；沒按住的時候，照按鍵 2 的開關
        if button1_now == 1:
            leds.fill(RED)
        elif light_is_on:
            leds.fill(WHITE)
        else:
            leds.fill(OFF)
        leds.write()

        # 每圈休息 0.02 秒。拿掉會怎樣？
        #   · 彩燈要「安靜一下下」才會顯示新顏色；一直 write() 不停，燈就來不及更新
        #   · 按鍵按下時會抖動，太快讀會被算成按了好幾次
        time.sleep(0.02)
finally:
    leds.fill(OFF)
    leds.write()
