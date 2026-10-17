/* mango-ble.js — MANGO 的 Web Bluetooth 小工具庫（做 TODO 不用改；新增藍牙功能時要在 MANGO_CHARS 加一行）
 *
 * 用法：
 *   const mango = new MangoBLE();
 *   await mango.connect();                       // 跳出藍牙裝置選單
 *   await mango.write("led", [255, 255, 0, 0]);  // 寫入 bytes
 *   await mango.writeFast("brightness", [50]);   // 快速寫入（不等回覆，拖滑桿用）
 *   const data = await mango.read("brightness"); // 讀出 DataView
 *   await mango.subscribe("keys", (data) => { ... data.getUint8(0) ... });
 *
 * 特徵值名稱與資料格式（和 board/mango_ble.py 一致）：
 *   led         寫 4 bytes [index, R, G, B]（index 255 = 全部）；讀 18 bytes
 *   brightness  1 byte 0~100
 *   effect      1 byte：0 靜態、1 彩虹、2 呼吸、3 跑馬燈、4 警示燈
 *   buzzer      4 bytes：頻率 uint16 小端序 + 毫秒 uint16 小端序
 *   keys        1 byte：bit0 = Key1、bit1 = Key2（notify）
 *   game        寫 1 byte：1 = 開始；notify int16 小端序：反應時間毫秒，-1 = 偷跑
 *
 * 新增功能：在下面的 MANGO_CHARS 加一行「名稱: UUID」，UUID 中間的 4 碼要和 board/mango_ble.py 一樣
 */
const MANGO_SERVICE = "4d414e47-4f58-3400-8000-000000000000";
const MANGO_CHARS = {
  led: "4d414e47-4f58-3401-8000-000000000000",
  brightness: "4d414e47-4f58-3402-8000-000000000000",
  effect: "4d414e47-4f58-3403-8000-000000000000",
  buzzer: "4d414e47-4f58-3404-8000-000000000000",
  keys: "4d414e47-4f58-3405-8000-000000000000",
  game: "4d414e47-4f58-3406-8000-000000000000",
};

class MangoBLE {
  constructor() {
    this.device = null;
    this.chars = {};
    this._queue = Promise.resolve();
    /** 連線狀態改變時呼叫：(connected: boolean, name: string) => void */
    this.onConnectionChange = () => {};
    /** 每次收送資料都會呼叫，方便顯示「通訊紀錄」：(text: string) => void */
    this.onLog = () => {};
  }

  static get supported() {
    return !!navigator.bluetooth;
  }

  get connected() {
    return !!(this.device && this.device.gatt.connected);
  }

  async connect() {
    if (!MangoBLE.supported) {
      throw new Error("這個瀏覽器不支援 Web Bluetooth，請用電腦版 Chrome 或 Edge");
    }
    this.device = await navigator.bluetooth.requestDevice({
      filters: [{ namePrefix: "MANGO" }],
      optionalServices: [MANGO_SERVICE],
    });
    this.device.addEventListener("gattserverdisconnected", () => {
      this.chars = {};
      this.onLog("✗ 已斷線");
      this.onConnectionChange(false, this.device.name);
    });
    this.onLog(`… 連線到 ${this.device.name}`);
    const server = await this.device.gatt.connect();
    const service = await server.getPrimaryService(MANGO_SERVICE);
    for (const [name, uuid] of Object.entries(MANGO_CHARS)) {
      try {
        this.chars[name] = await service.getCharacteristic(uuid);
      } catch (e) {
        // 網頁加了新功能、板子還沒有：其他功能照常可以用
        this.onLog(`⚠ 板子沒有「${name}」：mango_ble.py 有加同一個編號嗎？改完要重新 Upload File to Board`);
      }
    }
    this.onLog("✓ 已連線");
    this.onConnectionChange(true, this.device.name);
  }

  disconnect() {
    if (this.connected) this.device.gatt.disconnect();
  }

  /** 寫入 bytes。bytes 可以是陣列 [1, 2, 3] 或 Uint8Array。 */
  write(name, bytes) {
    const data = Uint8Array.from(bytes);
    for (const b of bytes) {
      if (!Number.isInteger(b) || b < 0 || b > 255) {
        // JSON.stringify 讓字串顯示成 "2"，學生才看得出是忘了 Number()
        return Promise.reject(new Error(`${name}：每個 byte 必須是 0~255 的整數，收到 ${JSON.stringify(b)}`));
      }
    }
    return this._run(async () => {
      await this._char(name).writeValueWithResponse(data);
      this.onLog(`→ ${name}: ${MangoBLE.hex(data)}`);
    });
  }

  /** 快速寫入：不等板子回覆，給拖滑桿這種「連續送出、只在乎最新值」的資料用。
   *  板子端的特徵值要開 write_no_response（mango_ble.py 的亮度就是）；沒開的話自動改用一般寫入。 */
  writeFast(name, bytes) {
    const data = Uint8Array.from(bytes);
    return this._run(async () => {
      const c = this._char(name);
      if (c.properties.writeWithoutResponse) await c.writeValueWithoutResponse(data);
      else await c.writeValueWithResponse(data);
      this.onLog(`→ ${name}: ${MangoBLE.hex(data)}`);
    });
  }

  /** 讀取特徵值，回傳 DataView（用 getUint8(i)、getInt16(0, true) 等方法解讀）。 */
  read(name) {
    return this._run(async () => {
      const value = await this._char(name).readValue();
      this.onLog(`⇠ ${name}: ${MangoBLE.hex(value)}`);
      return value;
    });
  }

  /** 訂閱通知：板子每次 notify，callback(DataView) 就會被呼叫。 */
  subscribe(name, callback) {
    return this._run(async () => {
      const c = this._char(name);
      c.addEventListener("characteristicvaluechanged", (e) => {
        this.onLog(`← ${name}: ${MangoBLE.hex(e.target.value)}`);
        callback(e.target.value);
      });
      await c.startNotifications();
      this.onLog(`✓ 已訂閱 ${name}`);
    });
  }

  // ---------- 小工具 ----------

  /** 數字 → 2 bytes 小端序，例如 880 → [0x70, 0x03] */
  static u16(n) {
    return [n & 0xff, (n >> 8) & 0xff];
  }

  /** "#ff8800" → [255, 136, 0] */
  static hexToRgb(hex) {
    return [1, 3, 5].map((i) => parseInt(hex.substr(i, 2), 16));
  }

  /** [255, 136, 0] → "#ff8800" */
  static rgbToHex(rgb) {
    return "#" + rgb.map((v) => v.toString(16).padStart(2, "0")).join("");
  }

  /** bytes 或 DataView → "FF 88 00" */
  static hex(data) {
    const u8 = data instanceof DataView ? new Uint8Array(data.buffer, data.byteOffset, data.byteLength) : data;
    return Array.from(u8, (b) => b.toString(16).padStart(2, "0").toUpperCase()).join(" ");
  }

  // ---------- 內部 ----------

  _char(name) {
    if (!this.connected) throw new Error("尚未連線");
    const c = this.chars[name];
    if (!c) throw new Error(`板子沒有「${name}」這個功能：mango-ble.js、mango_ble.py 都加了同一個編號嗎？有重新 Upload 嗎？`);
    return c;
  }

  /* Web Bluetooth 同一時間只能進行一個 GATT 操作，
     連續快速寫入（例如拖動滑桿）會出現 "GATT operation already in progress"，
     所以把所有操作排隊，一個做完才做下一個。 */
  _run(fn) {
    const p = this._queue.then(fn);
    this._queue = p.catch(() => {});
    return p;
  }
}
