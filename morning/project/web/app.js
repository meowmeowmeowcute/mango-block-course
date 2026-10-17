/* app.js — 儀表板的「按下去做什麼」
 *
 * 做 TODO 不用改這個檔案；自由發揮時可以改。結構：
 *   1. 連線、連線後要做的事（讀目前狀態、訂閱板子的通知）
 *   2. 每張卡片的 onclick：用 mango.write("名稱", [bytes]) 傳給板子
 *      名稱和格式寫在 mango-ble.js 最上面；板子收到後會呼叫 dashboard.py 的函式
 *   3. 從板子收到的通知：mango.subscribe("名稱", callback)
 * 想加一個按鈕：index.html 加按鈕 → 這裡寫 $("你的id").onclick = safe(async () => { await mango.write(...) });
 */
const mango = new MangoBLE();
const $ = (id) => document.getElementById(id);

// 通訊紀錄
function log(text) {
  const time = new Date().toLocaleTimeString();
  $("log").textContent = `[${time}] ${text}\n` + $("log").textContent.slice(0, 5000);
}
mango.onLog = log;

// 包一層 try/catch：出錯時寫進通訊紀錄，而不是默默失敗
function safe(fn) {
  return async (...args) => {
    try {
      await fn(...args);
    } catch (e) {
      log("⚠ " + e.message);
    }
  };
}

// ---------- 1. 連線 ----------
$("connectBtn").onclick = safe(async () => {
  if (mango.connected) mango.disconnect();
  else await mango.connect();
});

mango.onConnectionChange = (connected, name) => {
  $("status").textContent = connected ? `已連線：${name}` : "未連線";
  $("status").classList.toggle("on", connected);
  $("connectBtn").textContent = connected ? "斷線" : "連線";
  if (connected) onConnected();
};

const onConnected = safe(async () => {
  // 讀取目前亮度
  const b = (await mango.read("brightness")).getUint8(0);
  $("brightness").value = b;
  $("brightnessValue").textContent = b;

  // 讀取 6 顆燈目前的顏色，更新圓點（18 bytes = 6 × RGB）
  const leds = await mango.read("led");
  document.querySelectorAll(".led-dot").forEach((dot, i) => {
    dot.style.background = MangoBLE.rgbToHex([leds.getUint8(i * 3), leds.getUint8(i * 3 + 1), leds.getUint8(i * 3 + 2)]);
  });

  // ---------- 3. 板子的通知 ----------
  // 按鍵：bit0 = Key1、bit1 = Key2（板子的 read_keys 決定）
  await mango.subscribe("keys", (data) => {
    const mask = data.getUint8(0);
    $("key1").classList.toggle("on", (mask & 1) !== 0);
    $("key2").classList.toggle("on", (mask & 2) !== 0);
  });

  // 小遊戲結果：int16，毫秒；-1 = 偷跑（板子的 mango_ble.game_result 送來）
  await mango.subscribe("game", (data) => {
    const ms = data.getInt16(0, true);
    $("gameMsg").textContent = ms < 0 ? "偷跑！再試一次" : `反應時間：${ms} ms`;
  });
});

// ---------- 2. 每張卡片的 onclick ----------
// 全部彩燈：index 255 = 全部
function setDots(hex) {
  document.querySelectorAll(".led-dot").forEach((d) => (d.style.background = hex));
}
$("allBtn").onclick = safe(async () => {
  const [r, g, b] = MangoBLE.hexToRgb($("allColor").value);
  await mango.write("led", [255, r, g, b]);
  setDots($("allColor").value);
});
$("offBtn").onclick = safe(async () => {
  await mango.write("led", [255, 0, 0, 0]);
  setDots("#000000");
});

// 單顆彩燈：index 0 ~ 5
document.querySelectorAll(".led-dot").forEach((dot) => {
  dot.onclick = safe(async () => {
    const index = Number(dot.dataset.index);
    const [r, g, b] = MangoBLE.hexToRgb($("dotColor").value);
    await mango.write("led", [index, r, g, b]);
    dot.style.background = $("dotColor").value;
  });
});

// 燈光效果：按鈕上的 data-effect 就是效果編號
document.querySelectorAll("[data-effect]").forEach((btn) => {
  btn.onclick = safe(async () => {
    await mango.write("effect", [Number(btn.dataset.effect)]);
  });
});

// 亮度：拖到哪裡就即時送出。
//   拖動時數值變很快，藍牙一次只能送一筆，所以「正在送」的時候只記住最新的值，
//   送完再送最新的那個，中間的值直接跳過。
let brightnessSending = false;
let brightnessPending = null;
async function sendBrightness() {
  brightnessSending = true;
  while (brightnessPending !== null) {
    const value = brightnessPending;
    brightnessPending = null;
    try {
      await mango.writeFast("brightness", [value]);
      await new Promise((r) => setTimeout(r, 30)); // 稍微喘口氣，避免把藍牙塞滿
    } catch (e) {
      log("⚠ " + e.message);
    }
  }
  brightnessSending = false;
}
$("brightness").addEventListener("input", (e) => {
  $("brightnessValue").textContent = e.target.value;
  if (!mango.connected) return;
  brightnessPending = Number(e.target.value);
  if (!brightnessSending) sendBrightness();
});

// 蜂鳴器：[頻率 2 bytes, 毫秒 2 bytes]，板子會呼叫 tone_on，時間到再 tone_off
function beep(freq, ms) {
  return mango.write("buzzer", [...MangoBLE.u16(freq), ...MangoBLE.u16(ms)]);
}
document.querySelectorAll("[data-freq]").forEach((btn) => {
  btn.onclick = safe(() => beep(Number(btn.dataset.freq), 250));
});

// 小遊戲：網頁只負責按「開始」和顯示結果，遊戲本身在板子端的 dashboard.py（小遊戲挑戰）
//   好處：反應時間是板子自己量的，不會被藍牙延遲影響
$("gameBtn").onclick = safe(async () => {
  $("gameMsg").textContent = "等綠燈…";
  await mango.write("game", [1]);
});
