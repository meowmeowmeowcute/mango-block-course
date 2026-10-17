"""
04 蜂鳴器：播一首歌
==================================================================
蜂鳴器只要記兩個數字（01 已經用過了）：
  buzzer.freq(音高)          數字越大，聲音越高（例如 440 = La）
  buzzer.duty_u16(音量)      0 = 安靜；3000 左右就夠大聲

歌譜就是一串「(音高, 秒數)」：
  song = [(DO, 0.4), (RE, 0.4), ...]
  程式只要從頭到尾，一個一個交給 play() 播出來。
  想換一首歌 → 只要改 song，不用改程式。

音高對照：Do 262、Re 294、Mi 330、Fa 349、Sol 392、La 440、Si 494、高音 Do 523
休止符（不發聲）：音高寫 0

動手改改看
  1. 把小星星後半段補完：Fa Fa Mi Mi Re Re Do
  2. 換成你自己會的一首歌
  ★ freq 和 duty_u16 會用在網頁儀表板實作的 TODO 3！
"""
import time

from machine import PWM, Pin

buzzer = PWM(Pin("BUZZER"))     # 板子上的蜂鳴器
VOLUME = 3000                   # 音量：0 = 安靜；3000 就夠大聲（最大約 32768，再大反而變小聲）

# 音高（頻率）
REST = 0                        # 休止符：不發聲
DO, RE, MI, FA, SOL, LA, SI = 262, 294, 330, 349, 392, 440, 494


def play(pitch, seconds):
    """播一個音：pitch 是音高，seconds 是這個音有幾秒"""
    if pitch != REST:
        buzzer.freq(pitch)          # 設定音高
        buzzer.duty_u16(VOLUME)     # 開始發聲
    time.sleep(seconds * 0.8)       # 響 80% 的時間
    buzzer.duty_u16(0)              # 停止
    time.sleep(seconds * 0.2)       # 安靜 20%，兩個一樣的音才分得開


# 小星星：一閃一閃亮晶晶
song = [
    (DO, 0.4), (DO, 0.4), (SOL, 0.4), (SOL, 0.4),
    (LA, 0.4), (LA, 0.4), (SOL, 0.8),
]

try:
    for pitch, seconds in song:     # 每次拿出一組 (音高, 秒數)，分別放進 pitch 和 seconds
        play(pitch, seconds)
finally:
    buzzer.duty_u16(0)              # 不管怎麼停下來，最後都關掉聲音
