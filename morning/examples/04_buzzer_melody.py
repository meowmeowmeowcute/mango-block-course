"""
04 蜂鳴器：播一首歌
==================================================================
複習：01 已經用過蜂鳴器了，只要記兩個數字（PWM 的原理這堂課先不深入）

  buzzer.freq(頻率)       頻率 = 音高，數字越大聲音越高（例如 440 = La）
  buzzer.duty_u16(音量)   0 = 安靜；3000 左右就夠大聲
  發聲 → 等一下 → 音量設成 0 停止（寫在 finally 裡，按 Stop 也會停）

觀念：把「資料」和「程式」分開 —— 歌譜放在串列裡，程式只負責一個一個播

  song = [(音高, 長度), (音高, 長度), ...]
  音高 0 代表休止符（不發聲）

  音高對照：Do 262、Re 294、Mi 330、Fa 349、Sol 392、La 440、Si 494、高音 Do 523

動手改改看
  1. 把小星星後半段補完：Fa Fa Mi Mi Re Re Do
  2. 換成你自己會的一首歌
  3. 讓每播一個音，就亮一顆彩燈
  ★ freq 和 duty_u16 之後會用在網頁儀表板實作的 TODO 3！
"""
import time

from machine import PWM, Pin

buzzer = PWM(Pin("BUZZER"))

DO, RE, MI, FA, SOL, LA = 262, 294, 330, 349, 392, 440

# 小星星：一閃一閃亮晶晶
song = [
    (DO, 0.4), (DO, 0.4), (SOL, 0.4), (SOL, 0.4),
    (LA, 0.4), (LA, 0.4), (SOL, 0.8),
]

try:
    for pitch, length in song:
        if pitch > 0:
            buzzer.freq(pitch)
            buzzer.duty_u16(3000)
        time.sleep(length * 0.8)    # 響 80% 的時間
        buzzer.duty_u16(0)
        time.sleep(length * 0.2)    # 安靜 20%，兩個一樣的音才分得開
finally:
    buzzer.duty_u16(0)
