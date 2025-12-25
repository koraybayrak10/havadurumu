from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import httpx

app = FastAPI(title="Stateless Weather API", version="1.0.0")

# Basit şehir -> koordinat eşlemesi (stateless: DB yok, dosya yok)
CITY_COORDS = {
    "istanbul": {"name": "İstanbul", "lat": 41.0082, "lon": 28.9784},
    "ankara": {"name": "Ankara", "lat": 39.9334, "lon": 32.8597},
    "izmir": {"name": "İzmir", "lat": 38.4237, "lon": 27.1428},
    "bursa": {"name": "Bursa", "lat": 40.1950, "lon": 29.0600},
    "antalya": {"name": "Antalya", "lat": 36.8969, "lon": 30.7133},
}

HTML = """
<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Hava Durumu (Stateless)</title>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial; max-width: 720px; margin: 40px auto; padding: 0 16px; }
    .card { border: 1px solid #ddd; border-radius: 12px; padding: 18px; }
    select, button { padding: 10px 12px; border-radius: 10px; border: 1px solid #ccc; font-size: 16px; }
    button { cursor: pointer; }
    pre { background: #f7f7f7; padding: 12px; border-radius: 10px; overflow: auto; }
    .row { display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
    small { color:#555; }
  </style>
</head>
<body>
  <h1>Güncel Hava Durumu</h1>
  <div class="card">
    <div class="row">
      <label for="city"><b>Şehir:</b></label>
      <select id="city">
        <option value="Istanbul">İstanbul</option>
        <option value="Ankara">Ankara</option>
        <option value="Izmir">İzmir</option>
        <option value="Bursa">Bursa</option>
        <option value="Antalya">Antalya</option>
      </select>
      <button onclick="loadWeather()">Getir</button>
    </div>
    <p id="status"><small>Seç ve “Getir”e bas.</small></p>
    <pre id="out">{}</pre>
    <p><small>API: <code>/api/weather?city=Istanbul</code></small></p>
  </div>

<script>
async function loadWeather() {
  const city = document.getElementById("city").value;
  const status = document.getElementById("status");
  const out = document.getElementById("out");

  status.innerHTML = "<small>Yükleniyor...</small>";
  out.textContent = "{}";

  try {
    const res = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Hata");
    status.innerHTML = `<small><b>${data.city}</b> için güncel veri alındı.</small>`;
    out.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    status.innerHTML = `<small style="color:#b00020">Hata: ${e.message}</small>`;
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
async def api_weather(
    city: str = Query(..., description="City name, e.g. Istanbul")
):
    key = city.strip().lower()
    if key not in CITY_COORDS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported city. Supported: {', '.join([v['name'] for v in CITY_COORDS.values()])}",
        )

    c = CITY_COORDS[key]
    lat, lon = c["lat"], c["lon"]

    # Open-Meteo current weather
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
