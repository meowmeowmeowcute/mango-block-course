"""
01 板子點名：確認環境裝好了
==================================================================
觀念：程式可以控制板子上的元件。這支先不用看懂，執行成功就代表環境裝好了。

怎麼執行：在 VS Code 打開這個檔案 → 按下方狀態列的「Run」。
看到什麼：6 顆彩燈依序亮起 → 嗶一聲 → 終端機印出板子資訊。
"""
import sys
import time

import neopixel
from machine import PWM, Pin

np = neopixel.NeoPixel(Pin("WS2812B"), 6)
buzzer = PWM(Pin("BUZZER"))

print("哈囉！我是", sys.implementation._machine)

# 彩燈依序亮起
for i in range(6):
    np[i] = (30, 10, 0)
    np.write()
    time.sleep(0.2)

# 嗶一聲
buzzer.freq(880)
buzzer.duty_u16(3000)
time.sleep(0.2)
buzzer.duty_u16(0)

time.sleep(1)
np.fill((0, 0, 0))
np.write()
print("環境 OK！")
