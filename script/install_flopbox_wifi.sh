#!/usr/bin/env bash
# install_flopbox_wifi.sh
# Provisioning Wi-Fi plug&play : SoftAP (hostapd) + dnsmasq + Flask (Gunicorn) derrière Nginx
# Usage: sudo bash install_flopbox_wifi.sh

set -euo pipefail

### === Config par défaut (tu peux modifier) ===
AP_SSID="${AP_SSID:-FLOPBOX-SETUP}"
AP_PSK="${AP_PSK:-flopbox123}"             # mot de passe du réseau AP provisoire
AP_NET="${AP_NET:-192.168.4.1/24}"         # réseau AP
AP_IP="${AP_IP:-192.168.4.1}"
AP_DHCP_RANGE="${AP_DHCP_RANGE:-192.168.4.2,192.168.4.20,255.255.255.0,24h}"
PORTAL_DOMAIN="${PORTAL_DOMAIN:-setup.flopbox}"
PORTAL_DIR="${PORTAL_DIR:-/opt/wifi-portal}"
GUNICORN_BIND="${GUNICORN_BIND:-127.0.0.1:5001}"
WLAN_IF="${WLAN_IF:-}"                     # si vide -> auto-détection
COUNTRY_CODE="${COUNTRY_CODE:-FR}"         # pour wpa_supplicant.conf

### === Fonctions utilitaires ===
need_root() {
  if [[ $EUID -ne 0 ]]; then
    echo "Ce script doit être lancé en root. Utilise: sudo bash $0"
    exit 1
  fi
}

detect_wlan() {
  if [[ -n "${WLAN_IF}" ]]; then
    echo "Interface Wi-Fi forcée: ${WLAN_IF}"
    return
  fi
  if command -v iw >/dev/null 2>&1; then
    local cand
    cand="$(iw dev 2>/dev/null | awk '/Interface/ {print $2; exit}')"
    if [[ -n "$cand" ]]; then
      WLAN_IF="$cand"
    fi
  fi
  if [[ -z "${WLAN_IF}" ]]; then
    # fallback courant sur Raspberry
    WLAN_IF="wlan0"
  fi
  echo "Interface Wi-Fi détectée: ${WLAN_IF}"
}

apt_install() {
  apt-get update
  DEBIAN_FRONTEND=noninteractive apt-get install -y \
    hostapd dnsmasq python3-venv python3-pip nginx curl
  systemctl disable hostapd || true
  systemctl disable dnsmasq || true
}

setup_flask() {
  mkdir -p "${PORTAL_DIR}"
  python3 -m venv "${PORTAL_DIR}/venv"
  "${PORTAL_DIR}/venv/bin/pip" install --upgrade pip
  "${PORTAL_DIR}/venv/bin/pip" install flask gunicorn

  cat > "${PORTAL_DIR}/app.py" <<'PY'
from flask import Flask, request, render_template_string
import subprocess, os

app = Flask(__name__)

HTML = """
<!doctype html>
<title>Configuration Wi-Fi FLOPBOX</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>
body { font-family: system-ui, Arial, sans-serif; margin: 2rem; max-width: 600px; }
label { display:block; margin:.5rem 0; }
input { width:100%; padding:.6rem; }
button { padding:.7rem 1rem; margin-top:1rem; cursor:pointer; }
.card { padding:1rem; border:1px solid #ddd; border-radius:12px; box-shadow:0 2px 6px rgba(0,0,0,.06); }
</style>
<h2>Connexion à votre Wi-Fi</h2>
<div class="card">
<form method="post">
  <label>Nom du réseau (SSID)
    <input name="ssid" placeholder="ex: Livebox-1234" required>
  </label>
  <label>Mot de passe
    <input name="psk" type="password" placeholder="Mot de passe du Wi-Fi" required>
  </label>
  <button type="submit">Configurer</button>
</form>
</div>
<p style="margin-top:1rem;color:#666;">Astuce : si la page captive ne s'ouvre pas, allez sur <b>http://setup.flopbox</b> ou <b>http://192.168.4.1</b>.</p>
"""

SUCCESS = """
<h3>Configuration enregistrée ✅</h3>
<p>Connexion en cours au réseau Wi-Fi...<br>Le point d'accès va se couper automatiquement.</p>
"""

COUNTRY=os.environ.get("PORTAL_COUNTRY","FR")

@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        ssid = (request.form.get("ssid") or "").strip()
        psk  = (request.form.get("psk")  or "").strip()
        wpa = f"""country={COUNTRY}
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={{
    ssid="{ssid}"
    psk="{psk}"
    key_mgmt=WPA-PSK
    priority=10
}}"""
        with open("/etc/wpa_supplicant/wpa_supplicant.conf","w") as f:
            f.write(wpa)
        os.chmod("/etc/wpa_supplicant/wpa_supplicant.conf", 0o600)
        # Essaye de reconfigurer sans reboot
        subprocess.run(["wpa_cli","-i", os.environ.get("PORTAL_WLAN","wlan0"), "reconfigure"])
        # Déclenche l'orchestrateur pour couper l'AP dès que connecté
        os.system("systemctl restart wifi-provision || true")
        return SUCCESS
    return render_template_string(HTML)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001)
PY

  chown -R root:root "${PORTAL_DIR}"
  chmod -R 755 "${PORTAL_DIR}"

  cat > /etc/systemd/system/wifi-portal.service <<EOF
[Unit]
Description=Wi-Fi Captive Portal Flask (Gunicorn)
After=network-online.target
Wants=network-online.target

[Service]
WorkingDirectory=${PORTAL_DIR}
Environment=PORTAL_WLAN=${WLAN_IF}
Environment=PORTAL_COUNTRY=${COUNTRY_CODE}
ExecStart=${PORTAL_DIR}/venv/bin/gunicorn -w 2 -b ${GUNICORN_BIND} app:app
User=root
Group=root
Restart=on-failure
RestartSec=2

[Install]
WantedBy=multi-user.target
EOF

  systemctl daemon-reload
  systemctl enable --now wifi-portal
}

setup_nginx() {
  # vhost dédié en default_server sur l'AP (pratique pour captive portal)
  cat > /etc/nginx/sites-available/setup <<EOF
server {
    listen 80 default_server;
    server_name ${PORTAL_DOMAIN} ${AP_IP};

    access_log /var/log/nginx/wifi-portal.access.log;
    error_log  /var/log/nginx/wifi-portal.error.log;

    location / {
        proxy_pass http://${GUNICORN_BIND};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_read_timeout 60s;
    }
}
EOF

  ln -sf /etc/nginx/sites-available/setup /etc/nginx/sites-enabled/setup
  nginx -t
  systemctl reload nginx
}

setup_hostapd_dnsmasq() {
  cat > /etc/hostapd/hostapd.conf <<EOF
interface=${WLAN_IF}
ssid=${AP_SSID}
hw_mode=g
channel=6
auth_algs=1
wmm_enabled=0
wpa=2
wpa_passphrase=${AP_PSK}
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
EOF

  mkdir -p /etc/dnsmasq.d
  cat > /etc/dnsmasq.d/provision.conf <<EOF
interface=${WLAN_IF}
dhcp-range=${AP_DHCP_RANGE}
dhcp-option=3,${AP_IP}
server=1.1.1.1
address=/${PORTAL_DOMAIN}/${AP_IP}
# (Optionnel) rediriger tout le DNS pendant le mode AP :
# address=/#/${AP_IP}
EOF

  # On laisse hostapd/dnsmasq désactivés au boot : l'orchestrateur les pilotera.
  systemctl disable hostapd || true
  systemctl disable dnsmasq || true
}

setup_orchestrator() {
  cat > /usr/local/bin/wifi-provision <<'BASH'
#!/usr/bin/env bash
set -euo pipefail

WLAN_IF="${WLAN_IF:-wlan0}"
AP_IP="${AP_IP:-192.168.4.1}"
PORTAL_SERVICE="${PORTAL_SERVICE:-wifi-portal}"

CHECK_WIFI() {
  # "Connecté" = route vers Internet
  ip route get 8.8.8.8 >/dev/null 2>&1
}

START_AP() {
  echo "[wifi-provision] Démarrage AP sur ${WLAN_IF} @ ${AP_IP}"
  ip link set "${WLAN_IF}" down || true
  ip addr flush dev "${WLAN_IF}" || true
  ip addr add "${AP_IP}/24" dev "${WLAN_IF}"
  ip link set "${WLAN_IF}" up
  systemctl start dnsmasq
  hostapd /etc/hostapd/hostapd.conf -B
  systemctl start "${PORTAL_SERVICE}"
}

STOP_AP() {
  echo "[wifi-provision] Arrêt AP"
  pkill hostapd || true
  systemctl stop dnsmasq || true
  ip addr flush dev "${WLAN_IF}" || true
}

main() {
  # Si déjà connecté, on s'assure de couper l'AP et on sort.
  if CHECK_WIFI; then
    echo "[wifi-provision] Déjà connecté. Rien à faire."
    STOP_AP || true
    exit 0
  fi

  START_AP

  echo "[wifi-provision] En attente de connexion Wi-Fi client..."
  # Boucle 15 min max (180 * 5s)
  for i in $(seq 1 180); do
    if CHECK_WIFI; then
      echo "[wifi-provision] Connecté ! On coupe l'AP."
      STOP_AP
      systemctl try-reload-or-restart nginx || true
      exit 0
    fi
    sleep 5
  done

  echo "[wifi-provision] Toujours pas de Wi-Fi client. On reste en mode AP."
}

main "$@"
BASH

  chmod +x /usr/local/bin/wifi-provision

  cat > /etc/systemd/system/wifi-provision.service <<EOF
[Unit]
Description=Wi-Fi Auto Provisioning Orchestrator
After=network.target

[Service]
Type=simple
Environment=WLAN_IF=${WLAN_IF}
Environment=AP_IP=${AP_IP}
ExecStart=/usr/local/bin/wifi-provision
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

  systemctl daemon-reload
  systemctl enable --now wifi-provision
}

final_tips() {
  echo
  echo "========================================================"
  echo " Installation terminée ✅"
  echo " - AP SSID         : ${AP_SSID}"
  echo " - AP Password     : ${AP_PSK}"
  echo " - AP IP/Network   : ${AP_IP} (${AP_NET})"
  echo " - Portal domain   : http://${PORTAL_DOMAIN} (ou http://${AP_IP})"
  echo " - Interface Wi-Fi : ${WLAN_IF}"
  echo
  echo "Commandes utiles :"
  echo "  journalctl -u wifi-portal -f          # logs Flask"
  echo "  journalctl -u wifi-provision -f       # logs orchestrateur"
  echo "  systemctl restart wifi-provision      # relancer le mode AP"
  echo "  rm /etc/wpa_supplicant/wpa_supplicant.conf && reboot   # reset Wi-Fi"
  echo "========================================================"
}

### === Main ===
need_root
detect_wlan
apt_install
setup_flask
setup_nginx
setup_hostapd_dnsmasq
setup_orchestrator
final_tips
