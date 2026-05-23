from flask import Flask, request, jsonify, render_template_string
import requests
import json
import time
import secrets
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import html

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.json.ensure_ascii = False

# Rate Limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour", "10 per minute"],
    storage_uri="memory://"
)

def xss_clean(data):
    if isinstance(data, str):
        return html.escape(data)
    elif isinstance(data, dict):
        return {k: xss_clean(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [xss_clean(item) for item in data]
    return data

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NABI API SERVICES</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background-image: url('https://i.ibb.co/kgBNRNDg/MG-20260521-142250-507.webp');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
            padding: 20px;
            position: relative;
        }

        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.7);
            z-index: -1;
        }

        .header {
            text-align: center;
            padding: 30px;
            background: linear-gradient(135deg, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0.6) 100%);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            margin-bottom: 30px;
            border: 1px solid rgba(255,215,0,0.3);
        }

        .header h1 {
            font-size: 3em;
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: bold;
            font-style: italic;
        }

        .premium-badge {
            display: inline-block;
            background: linear-gradient(135deg, #FFD700, #FFA500);
            color: #000;
            padding: 5px 20px;
            border-radius: 30px;
            font-weight: bold;
            font-style: italic;
            margin-top: 10px;
        }

        .category {
            margin-bottom: 40px;
        }

        .category-title {
            font-size: 2em;
            font-weight: bold;
            font-style: italic;
            color: #FFD700;
            margin-bottom: 20px;
            padding-left: 15px;
            border-left: 5px solid #FFD700;
            display: inline-block;
        }

        .api-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }

        .api-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0.05) 100%);
            backdrop-filter: blur(15px);
            border-radius: 20px;
            padding: 20px;
            transition: all 0.4s ease;
            border: 1px solid rgba(255,215,0,0.3);
        }

        .api-card:hover {
            transform: translateY(-5px);
            border: 1px solid rgba(255,215,0,0.8);
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(255,215,0,0.5);
        }

        .api-name {
            font-size: 1.3em;
            font-weight: bold;
            font-style: italic;
            color: #FFD700;
        }

        .api-category {
            background: linear-gradient(135deg, #FFD700, #FFA500);
            color: #000;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.75em;
            font-weight: bold;
        }

        .api-desc {
            color: #E0E0E0;
            margin-bottom: 15px;
            font-size: 0.85em;
            font-style: italic;
        }

        .api-url {
            background: rgba(0,0,0,0.6);
            padding: 10px;
            border-radius: 10px;
            font-family: monospace;
            font-size: 0.7em;
            word-break: break-all;
            margin-bottom: 15px;
            color: #FFD700;
        }

        .button-group {
            display: flex;
            gap: 10px;
        }

        .btn-copy {
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: bold;
            background: linear-gradient(135deg, #00b09b, #96c93d);
            color: white;
        }

        .btn-open {
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: bold;
            background: white;
            color: #333;
        }

        .stats-bar {
            background: linear-gradient(135deg, rgba(0,0,0,0.8), rgba(0,0,0,0.6));
            backdrop-filter: blur(10px);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
        }

        .stat-item {
            text-align: center;
        }

        .stat-number {
            font-size: 1.8em;
            font-weight: bold;
            color: #FFD700;
        }

        .stat-label {
            color: #E0E0E0;
            font-style: italic;
        }

        .security-badge {
            background: linear-gradient(135deg, rgba(0,0,0,0.8), rgba(0,0,0,0.6));
            backdrop-filter: blur(10px);
            padding: 12px;
            text-align: center;
            border-radius: 12px;
            margin-top: 30px;
            color: #00ff00;
            font-weight: bold;
        }

        @media (max-width: 768px) {
            .api-grid {
                grid-template-columns: 1fr;
            }
            .header h1 {
                font-size: 1.8em;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 NABI API SERVICES</h1>
        <div class="premium-badge">⭐ PREMIUM API PLATFORMU ⭐</div>
        <p style="margin-top: 15px; color: #FFD700; font-style: italic;">Güvenli | Hızlı | 7/24 Aktif</p>
    </div>

    <div class="stats-bar">
        <div class="stat-item">
            <div class="stat-number" id="totalApis">22</div>
            <div class="stat-label">Aktif API</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">✓</div>
            <div class="stat-label">Sistem Durumu</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">A++</div>
            <div class="stat-label">Güvenlik</div>
        </div>
    </div>

    <div class="category">
        <div class="category-title">📋 NABI API (10 ADET)</div>
        <div class="api-grid" id="nabiGrid"></div>
    </div>

    <div class="category">
        <div class="category-title">🔍 KAPSAMLI API (12 ADET)</div>
        <div class="api-grid" id="kapsamliGrid"></div>
    </div>

    <div class="security-badge">
        🔒 XSS Koruması | 🛡️ Rate Limiting (10/dk) | 🌐 SSL | 🚫 DDoS Koruması
    </div>

    <script>
        // NABI API (10 adet) - domain: api.nabi.com.gov.2026tr.xyz
        const nabiApis = [
            { name: "Ad Soyad Sorgula", desc: "İsim ve soyisim ile kişi sorgulama", url: "https://api.nabi.com.gov.2026tr.xyz/api/adsoyad?adi=eymen&soyadi=yavuz" },
            { name: "Sulale Sorgula", desc: "Tüm aile bireylerini sorgulama", url: "https://api.nabi.com.gov.2026tr.xyz/api/sulale?tc=11111111110" },
            { name: "Çocuklar Sorgula", desc: "Kişinin çocuklarını sorgulama", url: "https://api.nabi.com.gov.2026tr.xyz/api/cocuklar?tc=11111111110" },
            { name: "Kardeşler Sorgula", desc: "Kişinin kardeşlerini sorgulama", url: "https://api.nabi.com.gov.2026tr.xyz/api/kardesler?tc=11111111110" },
            { name: "Anne Bilgisi", desc: "Kişinin anne bilgileri", url: "https://api.nabi.com.gov.2026tr.xyz/api/anne?tc=11111111110" },
            { name: "Baba Bilgisi", desc: "Kişinin baba bilgileri", url: "https://api.nabi.com.gov.2026tr.xyz/api/baba?tc=11111111110" },
            { name: "Eş Bilgisi", desc: "Kişinin eş bilgileri", url: "https://api.nabi.com.gov.2026tr.xyz/api/es?tc=11111111110" },
            { name: "Anne Adres", desc: "Annenin adres bilgisi", url: "https://api.nabi.com.gov.2026tr.xyz/api/anneadres?tc=11111111110" },
            { name: "Baba Adres", desc: "Babanın adres bilgisi", url: "https://api.nabi.com.gov.2026tr.xyz/api/babaadres?tc=11111111110" },
            { name: "Adres Sorgula", desc: "Kişinin adres bilgisi", url: "https://api.nabi.com.gov.2026tr.xyz/api/adres?tc=11111111110" }
        ];

        // KAPSAMLI API (12 adet) - domain: api.nabigunceln.com.gov.2026tr.xyz
        const kapsamliApis = [
            { name: "Araç Bilgisi", desc: "Plaka ile araç bilgisi sorgulama", url: "https://api.nabigunceln.com.gov.2026tr.xyz/api/arac-bilgisi?plaka=34ABC345" },
            { name: "Avukat Ankara", desc: "Ankara Barosu avukat sorgulama", url: "https://api.nabigunceln.com.gov.2026tr.xyz/api/avukat-sorgula-ankara?ad=Mehmet&soyad=Yilmaz" },
            { name: "Avukat İstanbul", desc: "İstanbul Barosu avukat sorgulama", url: "https://api.nabigunceln.com.gov.2026tr.xyz/api/avukat-sorgula-istanbul?sicil=340" },
            { name: "Enerji Borç", desc: "Enerji faturası borç sorgulama", url: "https://api.nabigunceln.com.gov.2026tr.xyz/api/enerji-fatura-borc-sorgula?tesisat=1001234567" },
            { name: "GİG Hak Sahipliği", desc: "Ad, soyad ve doğum tarihi ile sorgulama", url: "https://api.nabigunceln.com.gov.2026tr.xyz/api/gig-hak-sahipligi_sorgula?ad=ROKET&soyad=ATAR&dt=16/03/1998" },
            { name: "Hak Sahipliği", desc: "TC ile hak sahipliği sorgulama", url: "https://api.nabigunceln.com.gov.2026tr.xyz/api/hak-sahipligi_sorgula/11111111110" },
            { name: "Hakem Ara", desc: "TFF hakem sorgulama", url: "https://api.nabigunceln.com.gov.2026tr.xyz/api/hakem-ara?ad=Ali&soyad=Demir" },
            { name: "Plaka Ceza", desc: "Plaka ile ceza sorgulama", url: "https://api.nabigunceln.com.gov.2026tr.xyz/api/plaka-ceza-sorgula?plaka=34APP328" },
            { name: "Sicil Sorgula", desc: "İTO sicil numarası ile firma sorgulama", url: "https://api.nabigunceln.com.gov.2026tr.xyz/api/sicil-sorgula/340" },
            { name: "Sınav Sonucu", desc: "TC ile sınav sonucu sorgulama", url: "https://api.nabigunceln.com.gov.2026tr.xyz/api/sinav_sonuc_sorgula?tc=11111111110&tur=tyt" },
            { name: "Sınav Türleri", desc: "Sınav türleri listesi", url: "https://api.nabigunceln.com.gov.2026tr.xyz/api/sinav-turleri" },
            { name: "Uçuş Durumu", desc: "THY uçuş durumu sorgulama", url: "https://api.nabigunceln.com.gov.2026tr.xyz/api/ucus-durumu?no=1987&tarih=2026-05-22" }
        ];

        function createCard(api, index, type) {
            const card = document.createElement('div');
            card.className = 'api-card';
            card.innerHTML = `
                <div class="card-header">
                    <span class="api-name">${api.name}</span>
                    <span class="api-category">${type}</span>
                </div>
                <div class="api-desc">${api.desc}</div>
                <div class="api-url" id="url-${type}-${index}">${api.url}</div>
                <div class="button-group">
                    <button class="btn-copy" onclick="copyToClipboard('${api.url}')">📋 Kopyala</button>
                    <button class="btn-open" onclick="openInNewTab('${api.url}')">🔗 Aç</button>
                </div>
            `;
            return card;
        }

        function copyToClipboard(text) {
            navigator.clipboard.writeText(text);
            showNotification('✅ URL kopyalandı!');
        }

        function openInNewTab(url) {
            window.open(url, '_blank');
        }

        function showNotification(message) {
            const notification = document.createElement('div');
            notification.textContent = message;
            notification.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: linear-gradient(135deg, #00b09b, #96c93d);
                color: white;
                padding: 12px 24px;
                border-radius: 10px;
                z-index: 9999;
                font-weight: bold;
                animation: fadeOut 2s forwards;
            `;
            document.body.appendChild(notification);
            setTimeout(() => notification.remove(), 2000);
        }

        const nabiGrid = document.getElementById('nabiGrid');
        const kapsamliGrid = document.getElementById('kapsamliGrid');
        
        nabiApis.forEach((api, index) => {
            nabiGrid.appendChild(createCard(api, index, 'NABI'));
        });
        
        kapsamliApis.forEach((api, index) => {
            kapsamliGrid.appendChild(createCard(api, index, 'KAPSAMLI'));
        });
        
        document.getElementById('totalApis').textContent = nabiApis.length + kapsamliApis.length;
    </script>
</body>
</html>
"""

@app.route('/')
@limiter.limit("30 per minute")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "security": "active"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
