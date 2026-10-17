"""
02 控制彩燈：一顆、全部、跑馬燈
==================================================================
① 點亮一顆：先「設定」顏色，再「送出」
     leds[0] = RED     ← 只是先記下來，燈還不會變
     leds.write()      ← 這一行才真的送到燈上

② 設定全部：用 for 迴圈，一顆一顆設定，最後送出一次

③ 跑馬燈：全部關掉 → 點亮一顆 → 送出 → 等一下 → 換下一顆，一直重複

顏色的寫法：(紅, 綠, 藍)，每個數字 0 ~ 255。255 很刺眼，30 就夠亮了。

動手改改看
  1. 把 RED 改成 (0, 0, 30)，第 0 顆會變什麼顏色？
  2. 跑馬燈的 time.sleep(0.1) 改成 0.3 或 0.03，速度有什麼變化？
  3. 自己做一個新顏色，例如 PURPLE = (20, 0, 20)，讓跑馬燈用它
  ★ 這三個觀念都會用在網頁儀表板實作的 TODO 1 和 TODO 4！
"""
import time

import neopixel
from machine import Pin

leds = neopixel.NeoPixel(Pin("WS2812B"), 6)   # 板子上的 6 顆彩燈，編號 0 ~ 5

# 先幫常用的顏色取名字：(紅, 綠, 藍)
RED = (30, 0, 0)
GREEN = (0, 30, 0)
BLUE = (0, 0, 30)
OFF = (0, 0, 0)

# try / finally：按 Stop 時，程式可能停在任何一行；
#                 finally 裡的程式「一定」會執行，所以把關燈寫在那裡
try:
    # ① 點亮一顆
    leds[0] = RED            # 第 0 顆設成紅色（燈還不會變）
    leds.write()             # 送出！燈現在才亮
    time.sleep(1)

    # ② 用 for 迴圈設定全部
    for number in range(6):  # number 會依序是 0, 1, 2, 3, 4, 5
        leds[number] = BLUE  # 第 number 顆設成藍色
    leds.write()             # 6 顆都設定好，送出一次
    time.sleep(1)

    # ③ 跑馬燈（會一直跑，按左下角的「Stop」停止）
    while True:
        for number in range(6):
            leds.fill(OFF)           # 全部關掉
            leds[number] = GREEN     # 只點亮第 number 顆
            leds.write()             # 送出
            time.sleep(0.1)          # 等 0.1 秒，再換下一顆
finally:
    # 不管程式怎麼停下來，最後都會做這裡：關燈
    leds.fill(OFF)
    leds.write()
