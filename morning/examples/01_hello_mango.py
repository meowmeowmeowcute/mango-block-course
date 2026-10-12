"""
01 板子點名：確認環境裝好了
==================================================================
觀念：程式可以控制板子上的元件。這支先不用看懂，執行成功就代表環境裝好了。

怎麼執行：在 VS Code 打開這個檔案 → 按下方狀態列的「Run」。
看到什麼：6 顆彩燈亮起 → 嗶一聲 → 終端機印出板子資訊。

  「嗶一聲」那 4 行就是蜂鳴器的全部用法，04 播歌的時候會再回來看。
"""
import sys
import time

import neopixel
from machine import PWM, Pin

np = neopixel.NeoPixel(Pin("WS2812B"), 6)
buzzer = PWM(Pin("BUZZER"))

print("哈囉！我是", sys.implementation._machine)

# 彩燈全部亮起
np.fill((30, 10, 0))
np.write()

# 嗶一聲
buzzer.freq(880)        # 音高
buzzer.duty_u16(3000)   # 音量（開始發聲）
time.sleep(0.2)         # 響 0.2 秒
buzzer.duty_u16(0)      # 音量 0 = 停止

time.sleep(1)
np.fill((0, 0, 0))
np.write()
print("環境 OK！")
