/* app.js — MANGO X4 儀表板網頁（已完成，學生不用改） */
const mango = new MangoBLE();
const $ = (id) => document.getElementById(id);

// 通訊紀錄
function log(text) {
  const time = new Date().toLocaleTimeString();
  $("log").textContent = `[${time}] ${text}\n` + $("log").textContent.slice(0, 5000);
}
mango.onLog = log;

function safe(fn) {
  return async (...args) => {
    try {
      await fn(...args);
    } catch (e) {
      log("⚠ " + e.message);
    }
  };
}

// 連線
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

  // 訂閱按鍵
  await mango.subscribe("keys", (data) => {
    const mask = data.getUint8(0);
    const k1 = (mask & 1) !== 0;
    const k2 = (mask & 2) !== 0;
    $("key1").classList.toggle("on", k1);
    $("key2").classList.toggle("on", k2);
    if (k1) game.onKey1();
  });

  // 訂閱溫度
  await mango.subscribe("temp", (data) => {
    const t = data.getInt16(0, true) / 100;
    $("temp").textContent = t.toFixed(2);
    temps.push(t);
    if (temps.length > 60) temps.shift();
    drawChart();
  });
});

// 範例 A
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

// 單顆彩燈
document.querySelectorAll(".led-dot").forEach((dot) => {
  dot.onclick = safe(async () => {
    const index = Number(dot.dataset.index);
    const [r, g, b] = MangoBLE.hexToRgb($("dotColor").value);
    await mango.write("led", [index, r, g, b]);
    dot.style.background = $("dotColor").value;
  });
});

// 燈光效果
document.querySelectorAll("[data-effect]").forEach((btn) => {
  btn.onclick = safe(async () => {
    await mango.write("effect", [Number(btn.dataset.effect)]);
  });
});

// 亮度（拖動時只更新數字，放開才送出，避免塞爆藍牙）
$("brightness").addEventListener("input", (e) => {
  $("brightnessValue").textContent = e.target.value;
});
$("brightness").addEventListener("change", safe(async (e) => {
  await mango.write("brightness", [Number(e.target.value)]);
}));

// 蜂鳴器
function beep(freq, ms) {
  return mango.write("buzzer", [...MangoBLE.u16(freq), ...MangoBLE.u16(ms)]);
}
document.querySelectorAll("[data-freq]").forEach((btn) => {
  btn.onclick = safe(() => beep(Number(btn.dataset.freq), 250));
});

// 溫度折線圖
const temps = [];
function drawChart() {
  const c = $("tempChart");
  const dpr = window.devicePixelRatio || 1;
  c.width = c.clientWidth * dpr;
  c.height = c.clientHeight * dpr;
  const g = c.getContext("2d");
  g.clearRect(0, 0, c.width, c.height);
  if (temps.length < 2) return;
  let lo = Math.min(...temps), hi = Math.max(...temps);
  if (hi - lo < 1) { const m = (hi + lo) / 2; lo = m - 0.5; hi = m + 0.5; }
  const color = getComputedStyle(document.body).getPropertyValue("--accent");
  const mute = getComputedStyle(document.body).getPropertyValue("--mute");
  g.fillStyle = mute;
  g.font = `${11 * dpr}px sans-serif`;
  g.fillText(hi.toFixed(1), 0, 11 * dpr);
  g.fillText(lo.toFixed(1), 0, c.height - 2 * dpr);
  const left = 32 * dpr;
  g.strokeStyle = color;
  g.lineWidth = 2 * dpr;
  g.beginPath();
  temps.forEach((t, i) => {
    const x = left + (c.width - left) * i / 59;
    const y = c.height - 4 * dpr - (c.height - 16 * dpr) * (t - lo) / (hi - lo);
    i ? g.lineTo(x, y) : g.moveTo(x, y);
  });
  g.stroke();
}
window.addEventListener("resize", drawChart);

// 反應力遊戲
//   注意：量到的時間 = 你的反應時間 + 藍牙傳送延遲（約 15~50 ms），可以在報告裡討論
const game = {
  state: "idle", // idle → waiting（紅燈）→ go（綠燈）→ idle
  t0: 0,
  timer: null,

  start: safe(async () => {
    if (game.state !== "idle") return;
    game.state = "waiting";
    $("gameMsg").textContent = "等綠燈…";
    await mango.write("effect", [0]);
    await mango.write("led", [255, 255, 0, 0]);
    const delay = 2000 + Math.random() * 3000; // 隨機 2~5 秒，避免猜節奏
    game.timer = setTimeout(safe(async () => {
      await mango.write("led", [255, 0, 255, 0]);
      game.t0 = performance.now();
      game.state = "go";
    }), delay);
  }),

  onKey1: safe(async () => {
    if (game.state === "waiting") {
      clearTimeout(game.timer);
      game.state = "idle";
      $("gameMsg").textContent = "偷跑！再試一次";
      await beep(200, 400);
      await mango.write("led", [255, 0, 0, 0]);
    } else if (game.state === "go") {
      const ms = Math.round(performance.now() - game.t0);
      game.state = "idle";
      $("gameMsg").textContent = `反應時間：${ms} ms`;
      await beep(1320, 120);
      await mango.write("led", [255, 0, 0, 0]);
    }
  }),
};
$("gameBtn").onclick = game.start;
