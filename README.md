# BLBRG // TELEMETRY TERMINAL — IoT Sensor Surveillance

A professional, Bloomberg Terminal–style live dashboard web application for real-time IoT sensor telemetry monitoring, designed for high-density surveillance of Temperature, Humidity, and Ultrasonic Distance.

---

## ⚡ Quick Start

### 1. Launch the Dashboard
You can open `index.html` directly in any modern browser:
- **Direct open**: Double-click `index.html` in your file explorer, or
- **Local web server** (recommended):
  ```bash
  # Using Python 3:
  python -m http.server 8080

  # Or using Node:
  npx serve .
  ```
  Then navigate to `http://localhost:8080`.

### 2. Connect Your ThingSpeak Channel
You can configure your ThingSpeak channel in **two ways**:

#### Method A: Inside the UI (Recommended)
1. Click the **`[CONFIG]`** button in the top-right corner, or press **`F2`**.
2. Enter your:
   - **Channel ID** (e.g. `1234567`)
   - **Read API Key** (optional if the channel is public)
   - **Polling Interval** (default: `15s`)
   - **History Depth** (default: `50` points)
3. Click **`<CONNECT CHANNEL>`**. Settings persist automatically across browser reloads via `localStorage`.

#### Method B: Hardcode in `index.html`
Open `index.html` and edit the `DEFAULT_CONFIG` object located at the top of the `<script>` tag:
```javascript
const DEFAULT_CONFIG = {
  // Set your ThingSpeak Channel ID (e.g. '1234567')
  CHANNEL_ID: 'YOUR_CHANNEL_ID_HERE',

  // Set your ThingSpeak Read API Key (leave empty if public)
  READ_API_KEY: 'YOUR_READ_API_KEY_HERE',

  // Number of recent records to pull (30-50 recommended)
  RESULTS_LIMIT: 50,

  // Polling interval in seconds (ThingSpeak free tier is 15s)
  POLL_INTERVAL_SEC: 15,
};
```

---

## 🛰️ Sensor Field Specifications

| Metric | Field | Default Sensor | Unit | Accent Color | Nominal Range |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Temperature** | `field1` | DS18B20 1-Wire | °C | Phosphor Amber (`#ff9800`) | 18.0°C – 28.0°C |
| **Humidity** | `field2` | DHT22 / AM2302 | % RH | Telemetry Cyan (`#00e5ff`) | 40% – 70% |
| **Distance** | `field3` | HC-SR04 Ultrasonic | cm | Phosphor Green (`#00e676`) | > 30.0 cm |

---

## 🖥️ Terminal Features & Layout

1. **Top Bar & Command Prompt (`SYS_CMD`)**:
   - Live synchronized **UTC** and **Local** system clocks.
   - Live heartbeat connection indicator with real-time RTT latency and 15-second auto-poll countdown.
   - Functional Bloomberg Terminal command prompt (`SYS_CMD>`). Try typing:
     - `CONFIG` (opens configuration modal)
     - `SYNC` or `REFRESH` (forces immediate data cycle)
     - `PAUSE` / `RESUME` (stops/resumes feed)
     - `SIM` (switches to internal IoT simulator)
     - `CSV` (downloads telemetry buffer as CSV)
     - `CLEAR` (clears raw packet table)

2. **Ticker Summary Row**:
   - 3 large monospace numerical readouts with tabular figures (`tabular-nums`).
   - Dynamic delta indicators showing absolute change and percentage change ($\Delta$) since previous reading.
   - Real-time statistical metrics: `MIN`, `MAX`, `AVG`, and standard deviation ($\sigma$).
   - Auxiliary telemetry calculations: Dew point (°C) and ultrasonic echo time ($t_{echo} = \frac{2d}{v_{sound}}$).
   - Visual needle threshold gauge.

3. **Time-Series Chart Visualizers**:
   - Built on a custom high-performance HTML5 Canvas engine (zero external charting library dependencies).
   - Non-animated, instant-redraw terminal responsiveness.
   - 1px hairline dotted gridlines, threshold boundary limits, and emissive phosphor line traces.
   - Interactive crosshair reticle on hover snapping to exact timestamps and readings.
   - Quick timeframe selectors (`30P` / `50P`).

4. **Raw Telemetry Packet Log (RX_BUFFER)**:
   - Live scrolling tabular feed showing UTC timestamp, entry sequence ID, field readings, synthesized hex packet representation, RSSI signal strength, and checksum verification status.
   - Includes auto-scroll lock, buffer pause, clear, and one-click **CSV export**.

5. **Acoustic Feedback**:
   - Built-in retro terminal audio click synthesis using the native browser Web Audio API (toggleable via the top `AUDIO: ON/OFF` button). Zero external audio files required.

6. **Keyboard Shortcuts**:
   - `[F1]` : Help & Shortcut reference modal
   - `[F2]` : Channel Configuration dialog
   - `[F5]` : Force immediate ThingSpeak refresh cycle
   - `[SPACE]` : Pause / Resume telemetry feed
   - `[ESC]` : Close active modals or unfocus command prompt
