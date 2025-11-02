from flask import Flask, render_template_string

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>FLOP‑BOX • Dashboard</title>
  <style>
    :root{
      --bg:#f5f7fb;
      --card:#ffffff;
      --text:#0f172a;  /* slate-900 */
      --sub:#475569;   /* slate-600 */
      --muted:#94a3b8; /* slate-400 */
      --brand:#2563eb; /* blue-600 */
      --brand-700:#1d4ed8;
      --ok:#22c55e;    /* green-500 */
      --warn:#f59e0b;  /* amber-500 */
      --danger:#ef4444;/* red-500 */
      --ring:rgba(37,99,235,.35);
      --shadow:0 10px 25px rgba(2,6,23,.06), 0 2px 6px rgba(2,6,23,.06);
      --radius:14px;
    }
    *{box-sizing:border-box}
    html,body{height:100%}
    body{
      margin:0;background:var(--bg);color:var(--text);font:500 15px/1.45 system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
    }
    .app{max-width:1200px;margin:0 auto;padding:18px}
    /* Topbar */
    .topbar{
      background:#0b1220;color:#fff;border-radius:18px;padding:18px 22px;display:flex;align-items:center;gap:28px;box-shadow:var(--shadow);
    }
    .brand{font-weight:800;letter-spacing:.5px;font-size:26px}
    .tabs{display:flex;gap:22px;flex:1}
    .tab{color:#cbd5e1;text-decoration:none;font-weight:600;padding:10px 6px;border-bottom:2px solid transparent}
    .tab.active{color:#fff;border-color:#60a5fa}
    .avatar{margin-left:auto;width:34px;height:34px;border-radius:999px;background:#111827;display:grid;place-items:center;border:1px solid #1f2937}
    /* Layout */
    h2{margin:18px 6px}
    .grid{display:grid;grid-template-columns:1.2fr .9fr .8fr;gap:18px}
    @media (max-width:1040px){.grid{grid-template-columns:1fr 1fr}}
    @media (max-width:760px){.grid{grid-template-columns:1fr}}
    .card{background:var(--card);border-radius:var(--radius);box-shadow:var(--shadow);padding:18px}
    .section-title{font-size:22px;margin:18px 6px 8px}
    /* Lights */
    .lights .row{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}
    @media (max-width:520px){.lights .row{grid-template-columns:1fr}}
    .light{border:1px solid #e5e7eb;border-radius:12px;padding:14px;display:flex;gap:12px;align-items:center;justify-content:space-between}
    .light .name{display:flex;align-items:center;gap:12px;font-weight:600}
    .pill{display:inline-flex;align-items:center;gap:6px;background:#e2e8f0;border-radius:20px;padding:4px 10px;font-size:12px;font-weight:700;color:#334155}
    .pill.on{background:#dbeafe;color:#1d4ed8}
    .icon{width:18px;height:18px}
    /* Switch */
    .switch{--w:44px;--h:24px;position:relative;display:inline-block;width:var(--w);height:var(--h)}
    .switch input{display:none}
    .slider{position:absolute;cursor:pointer;inset:0;background:#e5e7eb;border-radius:999px;transition:.2s}
    .slider:before{content:"";position:absolute;height:18px;width:18px;left:3px;top:3px;background:#fff;border-radius:50%;box-shadow:0 1px 2px rgba(0,0,0,.2);transition:.2s}
    .switch input:checked + .slider{background:var(--brand)}
    .switch input:checked + .slider:before{transform:translateX(20px)}
    /* Climate & humidity */
    .stack{display:grid;gap:14px}
    .kv{display:flex;align-items:center;gap:12px;color:var(--sub)}
    .emph{font-size:34px;font-weight:800;color:var(--text)}
    .big{font-size:40px;font-weight:800}
    /* Energy chart */
    .chart{height:180px}
    .muted{color:var(--muted)}
    /* Automation lists */
    .auto-list{display:grid;gap:12px}
    .auto-item{border:1px solid #e5e7eb;border-radius:12px;padding:14px;display:flex;align-items:center;justify-content:space-between;gap:12px}
    .auto-item .left{display:flex;align-items:center;gap:12px}
    .badge{width:10px;height:10px;border-radius:999px;background:#93c5fd;box-shadow:0 0 0 3px #e0f2fe inset}
    .note{font-size:12px;color:var(--muted);margin-top:2px}
    /* Small helper */
    .row-2{display:grid;grid-template-columns:1fr 1fr;gap:18px}
    @media (max-width:640px){.row-2{grid-template-columns:1fr}}
    .spaced{display:flex;align-items:center;justify-content:space-between}
    .mt{margin-top:14px}
    .footer{color:#94a3b8;font-size:12px;text-align:center;margin:26px 0}
    /* Focus ring */
    .light:has(input:focus-visible), .auto-item:has(input:focus-visible), .switch:has(input:focus-visible), a:focus-visible{
      outline:3px solid var(--ring);outline-offset:2px
    }
  </style>
</head>
<body>
  <div class="app">
    <!-- Top bar -->
    <div class="topbar">
      <div class="brand">FLOP‑BOX</div>
      <nav class="tabs">
        <a class="tab active" href="#">Dashboard</a>
        <a class="tab" href="#">Devices</a>
        <a class="tab" href="#">Integrations</a>
        <a class="tab" href="#">Settings</a>
      </nav>
      <div class="avatar" title="Profil">
        <!-- simple avatar icon -->
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#9ca3af" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M20 21a8 8 0 0 0-16 0"/><circle cx="12" cy="7" r="4"/>
        </svg>
      </div>
    </div>

    <h2>Lights</h2>
    <div class="grid">
      <!-- Lights card -->
      <section class="card lights" style="grid-column: span 1">
        <div class="spaced">
          <div class="kv" style="font-weight:700;font-size:18px">Lampadaire Salon</div>
          <label class="switch" aria-label="Lampadaire Salon">
            <input type="checkbox" checked>
            <span class="slider"></span>
          </label>
        </div>
        <div class="row mt">
          <div class="light">
            <div class="name">
              <!-- bulb icon -->
              <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M2 10a10 10 0 1 1 20 0c0 3.87-2.69 6-4 7H6c-1.31-1-4-3.13-4-7Z"/></svg>
              <span>Plafonnier</span>
            </div>
            <span class="pill">OFF</span>
          </div>
          <div class="light">
            <div class="name">
              <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M2 10a10 10 0 1 1 20 0c0 3.87-2.69 6-4 7H6c-1.31-1-4-3.13-4-7Z"/></svg>
              <span>Lumière Cuisine</span>
            </div>
            <span class="pill">OFF</span>
          </div>
          <div class="light">
            <div class="name">
              <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M2 10a10 10 0 1 1 20 0c0 3.87-2.69 6-4 7H6c-1.31-1-4-3.13-4-7Z"/></svg>
              <span>Lumière Porche</span>
            </div>
            <span class="pill on">ON</span>
          </div>
          <div class="light">
            <div class="name">
              <svg class="icon" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6"/><path d="M10 22h4"/><path d="M2 10a10 10 0 1 1 20 0c0 3.87-2.69 6-4 7H6c-1.31-1-4-3.13-4-7Z"/></svg>
              <span>Porche 2</span>
            </div>
            <span class="pill on">ON</span>
          </div>
        </div>
      </section>

      <!-- Climate card -->
      <section class="card stack">
        <div style="font-weight:700;font-size:20px">Climat</div>
        <div class="kv"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v14"/><path d="M9 13a3 3 0 1 0 6 0"/></svg><span>Température</span></div>
        <div class="emph">21,5°C</div>
        <div class="kv"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="#f97316" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v14"/><path d="M9 13a3 3 0 1 0 6 0"/></svg><span>Mode</span></div>
        <div class="kv"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="#ea580c" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/></svg><strong>Auto</strong></div>
      </section>

      <!-- Humidity card -->
      <section class="card stack">
        <div class="kv" style="justify-content:space-between">
          <div class="kv"><svg class="icon" viewBox="0 0 24 24" fill="none" stroke="#0ea5e9" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2C8 7 5 10 5 13a7 7 0 1 0 14 0c0-3-3-6-7-11Z"/></svg><strong>Humidité</strong></div>
        </div>
        <div class="big">52%</div>
      </section>

      <!-- Energy card (span 2 cols on wide screens) -->
      <section class="card" style="grid-column: span 1">
        <div class="section-title">Énergie</div>
        <svg class="chart" viewBox="0 0 600 200" preserveAspectRatio="none" role="img" aria-label="Consommation horaire">
          <defs>
            <linearGradient id="fill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#93c5fd" stop-opacity="0.6"/>
              <stop offset="100%" stop-color="#93c5fd" stop-opacity="0.1"/>
            </linearGradient>
          </defs>
          <!-- Area -->
          <path d="M0 170 L40 160 L80 110 L120 140 L160 120 L200 150 L240 135 L280 155 L320 140 L360 170 L400 110 L440 60 L480 150 L520 120 L560 170 L600 170 L600 200 L0 200 Z" fill="url(#fill)"/>
          <!-- Line -->
          <polyline fill="none" stroke="#3b82f6" stroke-width="3" points="0,170 40,160 80,110 120,140 160,120 200,150 240,135 280,155 320,140 360,170 400,110 440,60 480,150 520,120 560,170 600,170"/>
        </svg>
        <div class="spaced muted" style="margin-top:-8px">
          <span>00:00</span><span>06:00</span><span>09:00</span><span>12:00</span>
        </div>
      </section>

      <!-- Automation (left) -->
      <section class="card">
        <div class="section-title">Automatisation</div>
        <div class="auto-list">
          <div class="auto-item">
            <div class="left"><span class="badge"></span>
              <div>
                <div style="font-weight:700">Mode Nuit</div>
                <div class="note">Active les lumières extérieures au crépuscule</div>
              </div>
            </div>
            <label class="switch"><input type="checkbox" checked><span class="slider"></span></label>
          </div>
          <div class="auto-item">
            <div class="left"><span class="badge"></span>
              <div>
                <div style="font-weight:700">Détection de Mouvement</div>
                <div class="note">Capteur couloir • État: inactif</div>
              </div>
            </div>
            <label class="switch"><input type="checkbox"><span class="slider"></span></label>
          </div>
          <div class="auto-item">
            <div class="left"><span class="badge"></span>
              <div>
                <div style="font-weight:700">Routine Matin</div>
                <div class="note">Ouvre les volets + 20°C</div>
              </div>
            </div>
            <label class="switch"><input type="checkbox"><span class="slider"></span></label>
          </div>
        </div>
      </section>

      <!-- Automation (right – compact switches like the mockup) -->
      <section class="card">
        <div class="section-title">Automatisation</div>
        <div class="row-2">
          <div>
            <div class="spaced"><strong>Mode Nuit</strong><label class="switch"><input type="checkbox" checked><span class="slider"></span></label></div>
          </div>
          <div>
            <div class="spaced"><strong>Détection Mouvement</strong><label class="switch"><input type="checkbox"><span class="slider"></span></label></div>
            <div class="note">Capteur Mouvement • OK</div>
          </div>
          <div>
            <div class="spaced"><strong>Routine Matin</strong><label class="switch"><input type="checkbox"><span class="slider"></span></label></div>
          </div>
          <div>
            <div class="spaced"><strong>Mode Absence</strong><label class="switch"><input type="checkbox"><span class="slider"></span></label></div>
          </div>
        </div>
      </section>
    </div>

    <div class="footer">UI statique d'exemple – branchez vos données/événements selon vos besoins.</div>
  </div>

  <script>
    // Demo: mettre à jour l'état ON/OFF des pastilles quand on clique une lumière
    document.querySelectorAll('.light .pill').forEach(pill => {
      pill.parentElement.addEventListener('click', () => {
        pill.classList.toggle('on');
        pill.textContent = pill.classList.contains('on') ? 'ON' : 'OFF';
      }, {passive:true});
      pill.style.cursor='pointer';
    });
  </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
