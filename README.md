# IoT REST API — Node-RED + MQTT + Custom Web Dashboard

**Mata Kuliah:** Pemrograman Internet of Things (SIF1502) — Pertemuan 9: REST API & Antarmuka Web IoT  
**Nama / NIM:** Riyanti Nafisa / 2410010250  
**Kelas:** 5M

Sistem monitoring & kontrol IoT: ESP32 (disimulasikan) → MQTT → Node-RED (backend REST API) → Web Dashboard buatan sendiri (HTML/CSS/JS).

```
ESP32 Simulator ──MQTT iot/sensor──▶ Node-RED ──▶ SQLite (history)
       ▲                                │  ├──▶ REST API  (GET/POST/PUT)  ──▶ Dashboard
       └────MQTT iot/kontrol, iot/alert─┘  └──▶ WebSocket (/ws/sensor)    ──▶ Dashboard (real-time)
```

## Struktur Repositori
```
node-red/flows.json            # flow backend (import ke Node-RED)
simulator/simulasi_esp32.py    # simulator ESP32 (publisher + subscriber kontrol)
dashboard/dashboard.html       # dashboard web
docs/                          # taruh screenshot hasil uji di sini
```

## Fitur
| Bagian | Status |
|---|---|
| A. MQTT Broker (Mosquitto lokal) | ✅ |
| B. Simulator ESP32 (paho-mqtt 2.x, `CallbackAPIVersion.VERSION2`) | ✅ |
| C. Flow Node-RED: `GET /api/suhu`, `GET /api/history`, `POST /api/kontrol`, CORS | ✅ |
| D. Custom Web Dashboard (fetch API) | ✅ |
| **Bonus 1** `PUT /api/threshold` + notifikasi saat suhu melewati batas | ✅ |
| **Bonus 2** Grafik real-time Chart.js | ✅ |
| **Bonus 3** Autentikasi API key via header `X-API-Key` | ✅ |
| **Bonus 4** WebSocket di Node-RED (update tanpa polling) | ✅ |
| **Bonus 5** History disimpan ke SQLite (bukan flow context) | ✅ |

## Cara Menjalankan
**1. Prasyarat:** Node-RED, Mosquitto, Python 3, browser modern.

**2. Install node SQLite** (sekali saja):
```bash
cd ~/.node-red          # Windows: C:\Users\<user>\.node-red
npm install node-red-node-sqlite
```
(atau lewat menu ☰ → *Manage palette* → *Install* → `node-red-node-sqlite`). Restart Node-RED.

**3. Import flow:** Node-RED → ☰ → Import → pilih `node-red/flows.json` → **Deploy**.
File database `iot_history.db` otomatis dibuat di folder kerja Node-RED.

**4. Jalankan komponen** (3 terminal):
```bash
mosquitto -v
node-red
pip install -r simulator/requirements.txt && python simulator/simulasi_esp32.py
```

**5. Buka dashboard:** buka http://localhost:1880/dashboard di browser
(disajikan langsung oleh Node-RED, tanpa masalah CORS).

## API
Semua endpoint wajib header **`X-API-Key`** (default `iot-kampus-2026`; ganti dengan environment variable `API_KEY` pada Node-RED).

| Endpoint | Method | Fungsi |
|---|---|---|
| `/api/suhu` | GET | Data sensor terakhir + status lampu + threshold |
| `/api/history?limit=50` | GET | History dari SQLite (default 50, maks 500) |
| `/api/kontrol` | POST | Kirim perintah ke ESP32 `{"device":"lamp","action":"on"}` (format `{"perintah":"ON"}` dari materi juga didukung) |
| `/api/threshold` | GET | Baca batas suhu |
| `/api/threshold` | PUT | Set batas suhu `{"suhu_max": 30}` |
| `ws://localhost:1880/ws/sensor` | WebSocket | Push event: `sensor`, `alert`, `lamp`, `threshold` |

```bash
KEY="X-API-Key: iot-kampus-2026"
curl -H "$KEY" http://localhost:1880/api/suhu
curl -H "$KEY" http://localhost:1880/api/history
curl -X POST http://localhost:1880/api/kontrol -H "$KEY" -H "Content-Type: application/json" -d '{"device":"lamp","action":"on"}'
curl -X PUT  http://localhost:1880/api/threshold -H "$KEY" -H "Content-Type: application/json" -d '{"suhu_max":28}'
curl http://localhost:1880/api/suhu        # tanpa key -> 401
```

## Verifikasi End-to-End
| Komponen | Hasil yang diharapkan |
|---|---|
| Simulator → MQTT | terminal simulator menampilkan `→ Publish: {...}` |
| MQTT → Node-RED | debug panel menampilkan data sensor |
| Node-RED → REST | `curl /api/suhu` mengembalikan JSON |
| REST/WS → Web | angka, grafik, dan tabel dashboard berubah |
| Web → REST → MQTT | klik tombol lampu → simulator menampilkan `← KONTROL diterima` |
| Threshold | set batas rendah (mis. 26) → banner 🚨 muncul di dashboard & simulator menampilkan `← ALERT` |

## Catatan Perbaikan dari Modul
- Flow ditambah node `tab` (`flow_api`) agar import tidak gagal.
- Typo header akibat pemotongan baris di PDF diperbaiki (`Access-Control-Allow-Origin`, `Access-Control-Allow-Headers`).
- Node "OPTIONS CORS" pada modul tidak berfungsi (node `http in` tidak mendukung method OPTIONS),
  sehingga dashboard disajikan dari Node-RED sendiri di /dashboard.

## Keterbatasan
- Endpoint WebSocket hanya memancarkan data (tidak menerima perintah) dan belum diautentikasi; autentikasi API key diterapkan pada seluruh endpoint REST.
- Nilai threshold disimpan di flow context (memori), kembali ke 30 °C setelah Node-RED restart.
- Tabel `sensor_history` tidak dibersihkan otomatis.

