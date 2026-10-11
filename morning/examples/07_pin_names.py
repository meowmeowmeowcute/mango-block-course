"""
07 認識 pin 腳
==================================================================
觀念：每個元件都接在晶片的某一支腳位（GPIO）上，程式要指定「哪一支腳」才能控制它

  Pin("KEY1")  和  Pin(30)  是同一支腳 —— KEY1 接在 GPIO 30
  本課程的韌體幫每支腳取了名字，用名字比較好讀、不容易寫錯。

  今天用到的腳位：
    名字        GPIO   接到
    WS2812B     45     6 顆彩燈
    BUZZER      46     蜂鳴器
    KEY1        30     按鍵 1
    KEY2        31     按鍵 2

  下午會用到的腳位（馬達）：M1A、M1B … M4B（GPIO 0 ~ 7）

  腳位有兩種用法：
    Pin.OUT  輸出：程式「送出」 0 / 1（控制燈、蜂鳴器、馬達）
    Pin.IN   輸入：程式「讀進」 0 / 1（讀按鈕）

動手改改看
  1. 把下面的 "KEY2" 也印出來
  2. 試試 Pin("M1A")，它是第幾號 GPIO？
"""
from machine import Pin

for name in ["WS2812B", "BUZZER", "KEY1"]:
    print(name, "→", Pin(name))

# 用名字和用號碼，讀到的是同一顆按鈕：按住 Key1 再執行一次看看
a = Pin("KEY1", Pin.IN, Pin.PULL_DOWN)
b = Pin(30, Pin.IN, Pin.PULL_DOWN)
print("用名字讀：", a.value(), "  用號碼讀：", b.value())
