"""
04 跑馬燈：讓燈動起來
==================================================================
觀念：動畫 = 一格一格畫
  ① 全部關掉 → ② 點亮「現在這一顆」 → ③ write() → ④ 等一下 → 換下一顆，重複

  按 VS Code 狀態列的「Stop」可以停止程式。
  finally 裡的程式「不管怎麼結束都會執行」，用來關燈。

動手改改看
  1. 把 time.sleep(0.1) 改成 0.3、0.03，速度有什麼變化？
  2. 改成從第 5 顆往第 0 顆跑（提示：range(5, -1, -1)）
  3. 讓「亮的那一顆」每跑一圈換一個顏色
  ★ 這個效果之後會用在 B4 專題的 TODO 4！
"""
import time

import neopixel
from machine import Pin

np = neopixel.NeoPixel(Pin("WS2812B"), 6)

try:
    while True:                     # 一直重複
        for i in range(6):
            np.fill((0, 0, 0))      # ① 全部關掉
            np[i] = (0, 30, 0)      # ② 只點亮第 i 顆
            np.write()              # ③ 送出
            time.sleep(0.1)         # ④ 等 0.1 秒
finally:
    np.fill((0, 0, 0))              # 停止時一定關燈
    np.write()
