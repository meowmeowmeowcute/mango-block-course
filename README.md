# MANGO X4 開發板課程

用 MicroPython 控制 MANGO X4 開發板（RP2350B + RM2 無線模組）。

| 資料夾 | 內容 |
|---|---|
| [`firmware/`](firmware/) | 課程用的 MicroPython 韌體（第一次使用前要先燒錄） |
| [`morning/`](morning/) | 上午：認識板子、LED 與按鈕、蜂鳴器與 pin 腳、藍牙網頁儀表板 |
| [`afternoon/`](afternoon/) | 下午：馬達 |

---

## 上課前的準備

### 1. 下載課程檔案

在本頁面右上方按 **Code → Download ZIP**，下載後解壓縮。
有安裝 git 的同學也可以用 `git clone`。

### 2. 需要的東西

- MANGO X4 開發板，以及一條**可以傳資料**的 USB Type-C 線（有些線只能充電）
- **有藍牙的筆電**（上午的專題會用到）
- 電腦版 **Chrome 或 Edge** 瀏覽器

### 3. 安裝軟體

1. **VS Code**：<https://code.visualstudio.com/>
2. **MicroPico 擴充功能**：打開 VS Code → 左邊的「擴充功能」→ 搜尋 `MicroPico` → 安裝。
   如果它建議安裝 Python 相關的擴充功能，也一起安裝。
3. **Python**：<https://www.python.org/downloads/>。安裝時要**勾選「Add python.exe to PATH」**。

### 4. 燒錄韌體（每塊板子只要做一次）

1. 用 USB 線接上板子。
2. **按住 BOOT 鍵 → 按一下 RESET 鍵 → 放開 BOOT 鍵**，電腦會出現一個名叫 `RP2350` 的磁碟。
3. 把 [`firmware/MANGO_X4-v1.29.0.uf2`](firmware/) 拖進這個磁碟。
4. 磁碟自動消失，就代表燒錄完成。

燒錄韌體不會清掉板子上原本存的檔案。

### 5. 用 VS Code 連接板子

1. VS Code → 檔案 → **開啟資料夾** → 選擇解壓縮後的課程資料夾。
2. 按 `Ctrl+Shift+P`，輸入 `MicroPico: Initialize MicroPico Project` 並執行。
3. 左下角的狀態列出現 **Pico Connected**，就代表連線成功。
4. 打開 `morning/examples/01_hello_mango.py`，按狀態列的 **Run**。
   彩燈亮起、嗶一聲，終端機印出「環境 OK！」就完成了 🎉

## MicroPico 的三個基本動作

| 動作 | 怎麼做 | 用途 |
|---|---|---|
| **Run** | 按狀態列的「Run」 | 把目前打開的檔案送到板子上執行（不會存進板子） |
| **Stop** | 按狀態列的「Stop」，或在終端機按 `Ctrl+C` | 停止正在執行的程式 |
| **Upload** | 在檔案上按右鍵 → **Upload File to Board** | 把檔案存進板子 |

> ⚠ 不要把自己的程式存成 `main.py` 上傳到板子，否則板子每次開機都會自動執行它。

## 連不上的時候

| 現象 | 解法 |
|---|---|
| 狀態列一直顯示 Pico Disconnected | 換一條可以傳資料的 USB 線；關掉 Thonny 等其他會佔用板子的程式；把板子拔掉再插回去 |
| 燒錄時沒有出現 `RP2350` 磁碟 | BOOT 鍵要一直按住，按完 RESET 之後才放開 |
| 執行後出現 `Pin("WS2812B")` 相關的錯誤 | 韌體不是課程版本，請重新燒錄 |
| 程式停不下來 | 在終端機按 `Ctrl+C`，或按板子上的 RESET 鍵 |
