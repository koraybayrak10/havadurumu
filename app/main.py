from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import httpx

app = FastAPI(title="Stateless Weather API", version="1.0.0")

CITY_COORDS = {
    "istanbul": {"name": "İstanbul", "lat": 41.0082, "lon": 28.9784},
    "ankara": {"name": "Ankara", "lat": 39.9334, "lon": 32.8597},
    "izmir": {"name": "İzmir", "lat": 38.4237, "lon": 27.1428},
    "bursa": {"name": "Bursa", "lat": 40.1950, "lon": 29.0600},
    "antalya": {"name": "Antalya", "lat": 36.8969, "lon": 30.7133},
}

HTML = r"""
<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Hava Durumu (Stateless)</title>

  <style>
    :root{
      --bg1:#0b1220;
      --bg2:#0f2a4a;
      --card: rgba(255,255,255,.10);
      --card2: rgba(255,255,255,.06);
      --text: rgba(255,255,255,.92);
      --muted: rgba(255,255,255,.68);
      --line: rgba(255,255,255,.16);
      --shadow: 0 18px 45px rgba(0,0,0,.35);
      --radius: 18px;
      --accent: #7c3aed;   /* mor */
      --accent2:#22c55e;   /* yeşil */
      --danger:#ff4d4f;
    }

    * { box-sizing: border-box; }
    body{
      margin:0;
      min-height:100vh;
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial;
      color: var(--text);
      background:
        radial-gradient(1000px 600px at 15% 10%, rgba(124,58,237,.35), transparent 60%),
        radial-gradient(900px 500px at 80% 25%, rgba(34,197,94,.22), transparent 60%),
        linear-gradient(180deg, var(--bg1), var(--bg2));
      display:flex;
      align-items:center;
      justify-content:center;
      padding: 28px 16px;
    }

    .container{
      width: min(920px, 100%);
      display:grid;
      gap: 18px;
    }

    header{
      display:flex;
      align-items:flex-end;
      justify-content:space-between;
      gap: 16px;
      flex-wrap:wrap;
    }

    .title{
      display:flex;
      flex-direction:column;
      gap: 6px;
    }

    h1{
      margin:0;
      font-size: clamp(24px, 2.8vw, 36px);
      letter-spacing: -0.02em;
      line-height:1.1;
    }

    .subtitle{
      color: var(--muted);
      font-size: 14px;
      line-height:1.4;
    }

    .pill{
      display:inline-flex;
      align-items:center;
      gap: 8px;
      padding: 8px 12px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,.06);
      border-radius: 999px;
      color: var(--muted);
      font-size: 13px;
      user-select:none;
    }

    .grid{
      display:grid;
      grid-template-columns: 1.1fr .9fr;
      gap: 18px;
    }

    @media (max-width: 860px){
      .grid{ grid-template-columns: 1fr; }
    }

    .card{
      border: 1px solid var(--line);
      background: linear-gradient(180deg, var(--card), var(--card2));
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
      padding: 18px;
      overflow:hidden;
      position:relative;
    }

    .card::before{
      content:"";
      position:absolute;
      inset:-2px;
      background:
        radial-gradient(500px 220px at 20% 0%, rgba(124,58,237,.20), transparent 60%),
        radial-gradient(520px 220px at 85% 20%, rgba(34,197,94,.18), transparent 60%);
      pointer-events:none;
      opacity:.75;
    }

    .card > * { position:relative; }

    .controls{
      display:flex;
      gap: 10px;
      align-items:center;
      flex-wrap:wrap;
      margin-top: 6px;
    }

    label{
      font-weight: 650;
      letter-spacing:.01em;
    }

    select{
      appearance:none;
      background: rgba(255,255,255,.08);
      border: 1px solid var(--line);
      color: var(--text);
      padding: 12px 14px;
      border-radius: 14px;
      font-size: 15px;
      outline:none;
      min-width: 220px;
    }

    select:focus{
      border-color: rgba(124,58,237,.55);
      box-shadow: 0 0 0 4px rgba(124,58,237,.18);
    }

    .btn{
      display:inline-flex;
      align-items:center;
      justify-content:center;
      gap: 10px;
      padding: 12px 14px;
      border-radius: 14px;
      border: 1px solid rgba(124,58,237,.45);
      background: linear-gradient(180deg, rgba(124,58,237,.92), rgba(124,58,237,.70));
      color: white;
      font-weight: 700;
      cursor: pointer;
      transition: transform .12s ease, filter .12s ease, box-shadow .12s ease;
      box-shadow: 0 10px 24px rgba(124,58,237,.18);
    }

    .btn:hover{ transform: translateY(-1px); filter: brightness(1.03); }
    .btn:active{ transform: translateY(0px) scale(.99); }

    .status{
      margin: 14px 0 12px;
      color: var(--muted);
      font-size: 14px;
      display:flex;
      align-items:center;
      gap: 10px;
    }

    .dot{
      width:10px;height:10px;border-radius:999px;
      background: rgba(255,255,255,.30);
      box-shadow: 0 0 0 3px rgba(255,255,255,.08);
    }

    .dot.ok{ background: var(--accent2); box-shadow: 0 0 0 3px rgba(34,197,94,.18); }
    .dot.err{ background: var(--danger); box-shadow: 0 0 0 3px rgba(255,77,79,.18); }

    .output{
      margin:0;
      padding: 14px;
      border-radius: 16px;
      border: 1px solid var(--line);
      background: rgba(10,18,32,.55);
      overflow:auto;
      max-height: 360px;
      font-size: 13px;
      line-height: 1.45;
    }

    code{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
      font-size: 0.95em;
      color: rgba(255,255,255,.86);
      background: rgba(255,255,255,.08);
      border: 1px solid rgba(255,255,255,.12);
      padding: 2px 8px;
      border-radius: 999px;
    }

    .meta{
      display:flex;
      flex-direction:column;
      gap: 12px;
    }

    .kpi{
      display:grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }

    @media (max-width: 520px){
      .kpi{ grid-template-columns: 1fr; }
      select{ min-width: 100%; }
      .btn{ width: 100%; }
    }

    .kpi .tile{
      border: 1px solid var(--line);
      background: rgba(255,255,255,.06);
      border-radius: 16px;
      padding: 12px 12px;
      display:flex;
      flex-direction:column;
      gap: 6px;
    }

    .tile .label{ color: var(--muted); font-size: 12px; }
    .tile .value{ font-size: 18px; font-weight: 780; letter-spacing:-0.01em; }

    .hint{
      color: var(--muted);
      font-size: 13px;
      line-height: 1.5;
    }

    .linkrow{
      display:flex;
      gap: 10px;
      flex-wrap:wrap;
      align-items:center;
    }

    a{
      color: rgba(255,255,255,.92);
      text-decoration: none;
      border-bottom: 1px dashed rgba(255,255,255,.30);
    }
    a:hover{ border-bottom-color: rgba(255,255,255,.65); }

    .small{
      font-size: 12.5px;
      color: var(--muted);
    }
  </style>
</head>

<body>
  <div class="container">
    <header>
      <div class="title">
        <h1>Güncel Hava Durumu</h1>
        <div class="subtitle">Stateless FastAPI + Open-Meteo. DB yok, dosya yok.</div>
      </div>
      <div class="pill">⚡ API: <span class="small"><code>/api/weather?city=Istanbul</code></span></div>
    </header>

    <div class="grid">
      <section class="card">
        <div class="controls">
          <label for="city">Şehir</label>
          <select id="city">
            <option value="Istanbul">İstanbul</option>
            <option value="Ankara">Ankara</option>
            <option value="Izmir">İzmir</option>
            <option value="Bursa">Bursa</option>
            <option value="Antalya">Antalya</option>
          </select>
          <button class="btn" onclick="loadWeather()">Getir</button>
        </div>

        <div class="status">
          <span id="dot" class="dot"></span>
          <span id="statusText">Seç ve “Getir”e bas.</span>
        </div>

        <pre id="out" class="output">{}</pre>

        <div class="hint" style="margin-top:12px">
          İpucu: Tarayıcıdan direkt çağır: <code>/api/weather?city=Istanbul</code>
        </div>
      </section>

      <aside class="card meta">
        <div class="kpi">
          <div class="tile">
            <div class="label">Sıcaklık</div>
            <div class="value" id="kpiTemp">—</div>
          </div>
          <div class="tile">
            <div class="label">Hissedilen</div>
            <div class="value" id="kpiFeels">—</div>
          </div>
          <div class="tile">
            <div class="label">Nem</div>
            <div class="value" id="kpiHum">—</div>
          </div>
          <div class="tile">
            <div class="label">Rüzgar</div>
            <div class="value" id="kpiWind">—</div>
          </div>
        </div>

        <div class="hint">
          Kaynak: <b>open-meteo.com</b><br/>
          Zaman: <span id="kpiTime">—</span>
        </div>

        <div class="linkrow small">
          <span>Health:</span> <a href="/health" target="_blank" rel="noreferrer">/health</a>
          <span>Docs:</span> <a href="/docs" target="_blank" rel="noreferrer">/docs</a>
        </div>
      </aside>
    </div>
  </div>

<script>
function setStatus(kind, text){
  const dot = document.getElementById("dot");
  const statusText = document.getElementById("statusText");
  dot.classList.remove("ok","err");
  if(kind === "ok") dot.classList.add("ok");
  if(kind === "err") dot.classList.add("err");
  statusText.textContent = text;
}

function setKpis(data){
  const t = (v, suf="") => (v === null || v === undefined) ? "—" : `${v}${suf}`;
  document.getElementById("kpiTemp").textContent  = t(data.temperature_c, "°C");
  document.getElementById("kpiFeels").textContent = t(data.feels_like_c, "°C");
  document.getElementById("kpiHum").textContent   = t(data.humidity_percent, "%");
  document.getElementById("kpiWind").textContent  = t(data.wind_kmh, " km/h");
  document.getElementById("kpiTime").textContent  = data.time || "—";
}

async function loadWeather() {
  const city = document.getElementById("city").value;
  const out = document.getElementById("out");

  setStatus("", "Yükleniyor...");
  out.textContent = "{}";
  setKpis({});

  try {
    const res = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Hata");
    setStatus("ok", `${data.city} için güncel veri alındı.`);
    out.textContent = JSON.stringify(data, null, 2);
    setKpis(data);
  } catch (e) {
    setStatus("err", `Hata: ${e.message}`);
  }
}
</script>
</body>
</html>
""".strip()


@app.get("/", response_class=HTMLResponse)
def home():
    return HTML


@app.get("/api/weather")
async def api_weather(city: str = Query(..., description="City name, e.g. Istanbul")):
    key = city.strip().lower()
    if key not in CITY_COORDS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported city. Supported: {', '.join([v['name'] for v in CITY_COORDS.values()])}",
        )

    c = CITY_COORDS[key]
    lat, lon = c["lat"], c["lon"]

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m"
        "&timezone=auto"
    )

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url)
        r.raise_for_status()
        data = r.json()

    current = data.get("current", {})
    payload = {
        "city": c["name"],
        "coords": {"lat": lat, "lon": lon},
        "time": current.get("time"),
        "temperature_c": current.get("temperature_2m"),
        "feels_like_c": current.get("apparent_temperature"),
        "humidity_percent": current.get("relative_humidity_2m"),
        "wind_kmh": current.get("wind_speed_10m"),
        "source": "open-meteo.com",
    }
    return JSONResponse(payload)


@app.get("/health")
def health():
    return {"ok": True}
