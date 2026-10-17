"""
01 板子點名：確認環境裝好了
==================================================================
這支程式先不用看懂，執行成功就代表環境裝好了。

怎麼執行：在 VS Code 打開這個檔案 → 按左下角狀態列的「Run」
會看到：  6 顆燈亮起 → 嗶一聲 → 下方終端機出現「環境 OK！」
"""
import time

import neopixel
from machine import PWM, Pin

leds = neopixel.NeoPixel(Pin("WS2812B"), 6)   # 板子上的 6 顆彩燈
buzzer = PWM(Pin("BUZZER"))                    # 板子上的蜂鳴器

print("哈囉！我是 MANGO BLOCK")

# 6 顆燈一起亮橘色
leds.fill((30, 10, 0))
leds.write()

# 嗶一聲（04 播歌的時候會再回來看這 4 行）
buzzer.freq(880)        # 音高
buzzer.duty_u16(3000)   # 音量：開始發聲
time.sleep(0.2)         # 響 0.2 秒
buzzer.duty_u16(0)      # 音量 0：停止

time.sleep(1)
leds.fill((0, 0, 0))    # 關燈
leds.write()
print("環境 OK！")
