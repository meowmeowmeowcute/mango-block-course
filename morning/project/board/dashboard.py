"""
網頁儀表板實作 —— 板子端（請完成 TODO 1 ~ 4）
==================================================================
實作 01~04：你寫的程式「自己從上跑到下」，Run 就看到結果。
這個檔案：你只要寫好「函式」，網頁按下按鈕時，工具庫 mango_ble.py 會幫你「呼叫」它們。

  TODO 1  on_led       網頁選顏色 → 存起來        和 02 的 for 迴圈一樣
  TODO 2  read_keys    回報按鍵有沒有被按          和 03 讀按鍵一樣
  TODO 3  tone_on/off  網頁琴鍵 → 蜂鳴器響        和 01 的嗶一聲一樣
  TODO 4  draw_chase   跑馬燈                      和 02 的跑馬燈一樣
  挑戰    小遊戲：反應力（做完 TODO 1~4 再來）

步驟：寫好 TODO → 先用最下面的 TEST_WITHOUT_WEB 自己測 → 再用網頁測
⚠ 這個檔案裡「不要」寫 time.sleep 或 while True（測試區除外），板子會卡住、網頁會斷線
"""
import random
import time

import neopixel
from machine import PWM, Pin

import mango_ble

# =====================================================================
# 板子上的元件（和範例一樣）
# =====================================================================
leds = neopixel.NeoPixel(Pin("WS2812B"), 6)          # 6 顆彩燈
buzzer = PWM(Pin("BUZZER"))                           # 蜂鳴器
buzzer.duty_u16(0)                                    # 一開始先靜音
button1 = Pin("KEY1", Pin.IN, Pin.PULL_DOWN)          # 按鍵 1
button2 = Pin("KEY2", Pin.IN, Pin.PULL_DOWN)          # 按鍵 2

VOLUME = 3000          # 蜂鳴器音量（和 04 一樣）
MAX_LEVEL = 0.5        # 就算亮度 100%，也只用一半，避免刺眼

# =====================================================================
# 網頁設定的值都存在這裡
# =====================================================================
led_colors = [(0, 0, 0)] * 6    # 6 顆燈各自的顏色，一開始都是黑的（關）
brightness = 30                 # 亮度 0 ~ 100
effect = 0                      # 現在的燈光效果編號：0 靜態 1 彩虹 2 呼吸 3 跑馬燈 4 警示燈


def apply_brightness(color):
    """把顏色照「亮度」調暗後回傳。網頁送來的顏色是 0~255，直接用太刺眼。（✅ 已完成）"""
    scale = brightness / 100 * MAX_LEVEL
    return (int(color[0] * scale), int(color[1] * scale), int(color[2] * scale))


# =====================================================================
# ✅ 範例：已經寫好了，先看懂再往下做
#   網頁拖亮度滑桿 → 工具庫呼叫 on_brightness(數字)
#   網頁按效果按鈕 → 工具庫呼叫 on_effect(編號)
#   要改「外面」的變數，前面要先寫 global
# =====================================================================
def on_brightness(value):
    global brightness
    brightness = value


def on_effect(effect_number):
    global effect
    effect = effect_number


# =====================================================================
# TODO 1：網頁選了顏色                              ← 和 02 的 for 迴圈一樣
#   led_number 是 0 ~ 5：只改那一顆   → led_colors[led_number] = (red, green, blue)
#   led_number 是 255  ：6 顆全部改   → 用 for 迴圈，6 顆都設成 (red, green, blue)
#   只要「存起來」就好，不用 leds.write()：tick 每 0.03 秒會把 led_colors 畫到燈上
#   ⚠ 不要寫 led_colors = [...]（那樣會變成新的變數，燈不會變，也不會有錯誤訊息）
# 測試：網頁先按「靜態」，再用「全部彩燈」選顏色按套用、點「單顆彩燈」的圓點
# =====================================================================
def on_led(led_number, red, green, blue):
    # 虛擬碼（用中文寫的步驟，一行一行翻成 Python）：
    #   如果 led_number 是 255：
    #       對每一顆 number（0 ~ 5）：
    #           led_colors[number] = (red, green, blue)
    #   否則：
    #       led_colors[led_number] = (red, green, blue)
    pass  # ← 刪掉這行，寫你的程式


# =====================================================================
# TODO 2：告訴工具庫兩顆按鍵有沒有被按               ← 和 03 讀按鍵一樣
#   要回傳兩個值：return 按鍵1的值, 按鍵2的值   （提示：button1.value()）
# 測試：按住板子上的 Key1 / Key2，網頁上的方塊要亮起來
# =====================================================================
def read_keys():
    # 虛擬碼：
    #   key1 = 讀 button1 的值
    #   key2 = 讀 button2 的值
    #   回傳 key1, key2
    return 0, 0  # ← 改成讀真正的按鍵


# =====================================================================
# TODO 3：蜂鳴器                                    ← 和 01 的「嗶一聲」一樣
#   tone_on(pitch)：設定音高 pitch，再用 VOLUME 開始發聲
#   tone_off()    ：停止發聲（音量設成 0）
#   ⚠ 不要寫 time.sleep：響多久由工具庫計時，時間到它會自動呼叫 tone_off()
# 測試：按網頁上的琴鍵。做完之後，連線／斷線時也會嗶一聲
# =====================================================================
def tone_on(pitch):
    # 虛擬碼：
    #   蜂鳴器的音高設成 pitch
    #   蜂鳴器的音量設成 VOLUME（開始發聲）
    pass


def tone_off():
    # 虛擬碼：
    #   蜂鳴器的音量設成 0（停止發聲）
    pass


# =====================================================================
# 燈光效果：每個函式負責畫「第 frame 格」畫面
#   frame 是第幾格（0, 1, 2, 3 …），工具庫每 0.03 秒呼叫一次 tick，frame 就加 1
#   函式裡只要設定 leds[...]
#   ⚠ 不要寫 time.sleep、while True，也不用 leds.write()：等待和送出都由 tick 負責
# =====================================================================
def draw_static(frame):
    """效果 0：靜態，照 led_colors 顯示（✅ 已完成）"""
    for number in range(6):
        leds[number] = apply_brightness(led_colors[number])


# =====================================================================
# TODO 4：效果 3 跑馬燈                              ← 和 02 的跑馬燈一樣
#   02 是自己用 for + time.sleep 換下一顆；這裡改成「看 frame 決定現在亮哪一顆」：
#   現在要亮第幾顆？ position = (frame // 4) % 6     （每 4 格換一顆，% 6 讓它在 0~5 之間繞圈）
#     第 position 顆 → apply_brightness(led_colors[position])
#     其他顆         → (0, 0, 0)
#   燈是黑的看不到？先用網頁「全部彩燈」設一個顏色
# 測試：網頁按「跑馬燈」
# =====================================================================
def draw_chase(frame):
    # 虛擬碼：
    #   position = (frame // 4) % 6           ← 現在輪到第幾顆
    #   對每一顆 number（0 ~ 5）：
    #       如果 number 是 position：leds[number] = apply_brightness(led_colors[position])
    #       否則：                   leds[number] = (0, 0, 0)
    pass


# ---- 以下效果已經寫好，可以讀讀看它們怎麼做 ---------------------------

RAINBOW = [(255, 0, 0), (255, 128, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (128, 0, 255)]


def draw_rainbow(frame):
    """效果 1：彩虹（✅ 已完成）6 顆燈各用一個顏色，每 4 格整排往前移一格"""
    shift = frame // 4
    for number in range(6):
        leds[number] = apply_brightness(RAINBOW[(number + shift) % 6])


def draw_breathe(frame):
    """效果 2：呼吸（✅ 已完成）100 格一輪：前 50 格慢慢變亮，後 50 格慢慢變暗"""
    step = frame % 100
    if step < 50:
        level = step / 50            # 0 → 1 變亮
    else:
        level = (100 - step) / 50    # 1 → 0 變暗
    for number in range(6):
        red, green, blue = apply_brightness(led_colors[number])
        leds[number] = (int(red * level), int(green * level), int(blue * level))


def draw_police(frame):
    """效果 4：警示燈（✅ 已完成）前 3 顆紅、後 3 顆藍，每 8 格互換"""
    red_first = (frame // 8) % 2 == 0
    for number in range(6):
        if (number < 3) == red_first:
            leds[number] = apply_brightness((255, 0, 0))
        else:
            leds[number] = apply_brightness((0, 0, 255))


# 順序 = 網頁按鈕的效果編號（0~4），不能調換
EFFECTS = [draw_static, draw_rainbow, draw_breathe, draw_chase, draw_police]


# =====================================================================
# 挑戰：小遊戲「反應力」（做完 TODO 1~4 再來）     ← 03 的「剛剛被按下」
#   網頁按「開始」→ 板子亮紅燈 → 隨機等 2~5 秒 → 變綠燈
#   綠燈之後按 Key1：反應時間 = 綠燈之後過了幾毫秒 → mango_ble.game_result(反應時間)
#   綠燈之前就按   ：偷跑 → mango_ble.game_result(-1)
#   time.ticks_ms()：板子的毫秒時鐘；time.ticks_diff(現在, 之前)：兩個時間差幾毫秒
# 測試：網頁「小遊戲：反應力」按「開始」
# =====================================================================
IDLE = "沒在玩"
RED_LIGHT = "紅燈"
GREEN_LIGHT = "綠燈"

game_state = IDLE         # 現在是 IDLE、RED_LIGHT 還是 GREEN_LIGHT
green_at_ms = 0           # 什麼時候要變綠燈（毫秒時鐘的時刻）
button1_before = 0        # 上一次讀到的按鍵 1（和 03 一樣，用來抓「剛剛被按下」）


def on_game_start():
    """網頁按「開始」時被呼叫（✅ 已完成）"""
    global game_state, green_at_ms, button1_before
    game_state = RED_LIGHT
    green_at_ms = time.ticks_add(time.ticks_ms(), random.randint(2000, 5000))
    button1_before = button1.value()


def draw_game(frame):
    global game_state, button1_before
    now = time.ticks_ms()

    # ① 時間到了就變綠燈（✅ 已完成）
    if game_state == RED_LIGHT and time.ticks_diff(now, green_at_ms) >= 0:
        game_state = GREEN_LIGHT

    # ② 挑戰：燈的顏色
    #    虛擬碼：
    #      如果 game_state 是 RED_LIGHT：6 顆紅 → leds.fill(apply_brightness((255, 0, 0)))
    #      否則：                        6 顆綠 → leds.fill(apply_brightness((0, 255, 0)))

    # ③ 挑戰：按鍵 1「剛剛被按下」了嗎？（和 03 的按鍵 2 一樣）
    #    虛擬碼：
    #      button1_now = 讀 button1 的值
    #      如果 button1_before 是 0 而且 button1_now 是 1：
    #          如果 game_state 是 RED_LIGHT：偷跑 → mango_ble.game_result(-1)
    #          否則：成功 → mango_ble.game_result(time.ticks_diff(now, green_at_ms))
    #          game_state = IDLE
    #      button1_before = button1_now
    #    加分：成功時 mango_ble.beep(1320, 120)、偷跑時 mango_ble.beep(200, 400)


def tick(frame):
    """工具庫每 0.03 秒呼叫一次：先全關，畫一格（燈光效果或小遊戲），再送出（✅ 已完成）"""
    leds.fill((0, 0, 0))             # 先全關：還沒寫好的效果會是黑的，不會卡在上一格
    if game_state == IDLE:
        EFFECTS[effect](frame)
    else:
        draw_game(frame)
    leds.write()


# =====================================================================
# 自由發揮：用 VS Code 內建的 AI Agent 一起做
#   想法：按住 Key2 變手電筒、發聲時燈也亮、網頁多一個按鈕……
#   要改網頁或新增藍牙功能，先看 mango_ble.py 最上面的「怎麼新增一個功能」，
#   以及 web/ 資料夾裡每個檔案開頭的說明。改了 mango_ble.py 要重新 Upload。
#   和 AI 合作是一個循環：描述想法 → 大致理解程式與重要觀念 → 除錯、重新定義需求
# =====================================================================


# =====================================================================
# 先不用網頁，自己呼叫看看（和實作 01~04 一樣：按 Run 就看到結果）
#   把 False 改成 True → Run：程式會「假裝自己是網頁」，依序呼叫你寫的函式
#   都對了 → 改回 False → Run → 換網頁來呼叫同一批函式
# =====================================================================
TEST_WITHOUT_WEB = False


def run_frames(seconds):
    """和工具庫做的事一樣：每 0.03 秒呼叫一次 tick(frame)。（測試區可以 sleep）"""
    for frame in range(int(seconds / 0.03)):
        tick(frame)
        time.sleep(0.03)


def test_without_web():
    print("① 測 TODO 1：on_led(255, 255, 0, 0) → 6 顆應該變紅")
    on_led(255, 255, 0, 0)
    run_frames(1)
    print("   on_led(0, 0, 0, 255) → 第 0 顆應該變藍")
    on_led(0, 0, 0, 255)
    run_frames(1)

    print("② 測 TODO 3：tone_on(440) → 應該嗶一聲")
    tone_on(440)
    time.sleep(0.3)
    tone_off()

    print("③ 測 TODO 2：接下來 5 秒，按按看 Key1 / Key2")
    last = None
    for _ in range(50):
        keys = read_keys()
        if keys != last:
            print("   read_keys() =", keys)
            last = keys
        time.sleep(0.1)

    print("④ 測 TODO 4：on_effect(3) → 跑馬燈跑 3 秒")
    on_effect(3)
    run_frames(3)

    leds.fill((0, 0, 0))
    leds.write()
    print("測試結束！都對了就把 TEST_WITHOUT_WEB 改回 False，用網頁試試")


# =====================================================================
# 啟動（不用改）
# =====================================================================
try:
    if TEST_WITHOUT_WEB:
        test_without_web()
    else:
        # 把上面寫好的函式交給工具庫：網頁按了什麼，工具庫就呼叫對應的函式
        mango_ble.run(
            on_led=on_led,
            on_brightness=on_brightness,
            on_effect=on_effect,
            tone_on=tone_on,
            tone_off=tone_off,
            read_keys=read_keys,
            tick=tick,
            on_game_start=on_game_start,
        )
finally:
    leds.fill((0, 0, 0))    # 按 Stop 時關燈、關蜂鳴器
    leds.write()
    buzzer.duty_u16(0)
