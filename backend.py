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

# Rate Limiting (DDoS koruması)
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

class NABIAPI:
    def __init__(self):
        self.base_url = "https://api.nabi.com.gov.2026tr.xyz"
    
    def sorgula(self, endpoint, **params):
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, params=params, timeout=15)
            return response.json() if response.status_code == 200 else {"hata": "API hatası"}
        except Exception as e:
            return {"hata": f"Bağlantı hatası: {str(e)}"}

class SorgulamaAPI:
    def __init__(self):
        self.base_url = "https://api.nabigunceln.com.gov.2026tr.xyz"
    
    def sorgula(self, endpoint, **params):
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, params=params, timeout=15)
            return response.json() if response.status_code == 200 else {"hata": "API hatası"}
        except Exception as e:
            return {"hata": f"Bağlantı hatası: {str(e)}"}

nabi = NABIAPI()
sorgu = SorgulamaAPI()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NABI API SERVICES - api.nabiservices.com.gov.2026tr.xyz</title>
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

        /* Siyah overlay */
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

        /* Header */
        .header {
            text-align: center;
            padding: 30px;
            background: linear-gradient(135deg, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0.6) 100%);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
            border: 1px solid rgba(255,215,0,0.3);
        }

        .header h1 {
            font-size: 3em;
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: bold;
            font-style: italic;
        }

        .domain {
            display: inline-block;
            background: linear-gradient(135deg, #FFD700, #FFA500);
            color: #000;
            padding: 5px 20px;
            border-radius: 30px;
            font-weight: bold;
            font-style: italic;
            margin-top: 10px;
            font-size: 0.9em;
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
            margin-left: 10px;
        }

        /* Kategori Başlıkları */
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
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            backdrop-filter: blur(5px);
            display: inline-block;
        }

        /* Grid Sistemi */
        .api-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }

        /* NABI Kartları - ARKA PLAN YOK (ŞEFFAF) */
        .nabi-card {
            background: transparent;
            backdrop-filter: none;
            border-radius: 20px;
            padding: 25px;
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
            cursor: pointer;
            box-shadow: none;
            border: 2px solid rgba(255,215,0,0.5);
        }

        .nabi-card:hover {
            transform: translateY(-5px);
            border: 2px solid rgba(255,215,0,0.9);
            background: rgba(0,0,0,0.3);
        }

        /* Sorgu Kartları - CAM EFEKTLİ */
        .sorgu-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0.05) 100%);
            backdrop-filter: blur(15px);
            border-radius: 20px;
            padding: 25px;
            transition: all 0.4s ease;
            position: relative;
            overflow: hidden;
            cursor: pointer;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            border: 1px solid rgba(255,215,0,0.3);
        }

        .sorgu-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 20px 40px rgba(0,0,0,0.5);
            border: 1px solid rgba(255,215,0,0.8);
            background: linear-gradient(135deg, rgba(255,255,255,0.25) 0%, rgba(255,255,255,0.1) 100%);
        }

        .sorgu-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,215,0,0.2), transparent);
            transition: left 0.6s;
        }

        .sorgu-card:hover::before {
            left: 100%;
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 12px;
            border-bottom: 2px solid rgba(255,215,0,0.5);
        }

        .api-name {
            font-size: 1.4em;
            font-weight: bold;
            font-style: italic;
            color: #FFD700;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }

        .api-category {
            background: linear-gradient(135deg, #FFD700, #FFA500);
            color: #000;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            font-style: italic;
        }

        .api-description {
            color: #E0E0E0;
            margin-bottom: 15px;
            font-size: 0.9em;
            line-height: 1.5;
            font-style: italic;
        }

        .api-url {
            background: rgba(0,0,0,0.6);
            padding: 12px;
            border-radius: 10px;
            font-family: monospace;
            font-size: 0.75em;
            word-break: break-all;
            margin-bottom: 15px;
            color: #FFD700;
            border: 1px solid rgba(255,215,0,0.3);
        }

        .button-group {
            display: flex;
            gap: 10px;
        }

        /* Kopyala butonu - YEŞİL */
        .btn-copy {
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: bold;
            font-style: italic;
            transition: all 0.3s;
            background: linear-gradient(135deg, #00b09b, #96c93d);
            color: white;
        }

        .btn-copy:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 20px rgba(0,176,155,0.4);
        }

        /* Aç butonu - BEYAZ */
        .btn-open {
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: bold;
            font-style: italic;
            transition: all 0.3s;
            background: white;
            color: #333;
        }

        .btn-open:hover {
            transform: scale(1.05);
            background: #f0f0f0;
            box-shadow: 0 5px 20px rgba(255,255,255,0.3);
        }

        /* Parametre butonu */
        .btn-param {
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: bold;
            font-style: italic;
            transition: all 0.3s;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }

        .btn-param:hover {
            transform: scale(1.05);
        }

        .param-input {
            margin-top: 15px;
            padding: 15px;
            background: rgba(0,0,0,0.6);
            border-radius: 12px;
            display: none;
            border: 1px solid rgba(255,215,0,0.3);
        }

        .param-input.active {
            display: block;
            animation: slideDown 0.3s ease;
        }

        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .param-group {
            margin-bottom: 12px;
        }

        .param-group label {
            display: block;
            margin-bottom: 5px;
            color: #FFD700;
            font-weight: bold;
            font-style: italic;
        }

        .param-group input {
            width: 100%;
            padding: 10px;
            border: 1px solid rgba(255,215,0,0.5);
            border-radius: 8px;
            background: rgba(255,255,255,0.9);
            color: #000;
            font-weight: bold;
        }

        .btn-test {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            width: 100%;
            margin-top: 10px;
            padding: 10px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-weight: bold;
            font-style: italic;
        }

        .btn-test:hover {
            transform: scale(1.02);
        }

        .result-area {
            margin-top: 15px;
            padding: 12px;
            background: rgba(0,0,0,0.8);
            border-radius: 10px;
            display: none;
            max-height: 250px;
            overflow: auto;
            border: 1px solid rgba(255,215,0,0.3);
        }

        .result-area.active {
            display: block;
        }

        .result-area pre {
            font-size: 0.75em;
            white-space: pre-wrap;
            word-wrap: break-word;
            color: #00ff00;
            font-family: monospace;
        }

        /* Stat Bar */
        .stats-bar {
            background: linear-gradient(135deg, rgba(0,0,0,0.8), rgba(0,0,0,0.6));
            backdrop-filter: blur(10px);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
            border: 1px solid rgba(255,215,0,0.3);
        }

        .stat-item {
            text-align: center;
        }

        .stat-number {
            font-size: 1.8em;
            font-weight: bold;
            font-style: italic;
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
            font-size: 0.85em;
            color: #00ff00;
            border: 1px solid rgba(0,255,0,0.3);
            font-weight: bold;
            font-style: italic;
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
        <div>
            <span class="domain">🌐 api.nabiservices.com.gov.2026tr.xyz</span>
            <span class="premium-badge">⭐ PREMIUM PLATFORM ⭐</span>
        </div>
        <p style="margin-top: 15px; color: #FFD700; font-style: italic; font-weight: bold;">Güvenli | Hızlı | 7/24 Aktif</p>
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
        <div class="category-title">📋 NABI VERİ SORGULAMA</div>
        <div class="api-grid" id="nabiGrid"></div>
    </div>

    <div class="category">
        <div class="category-title">🔍 KAPSAMLI SORGULAMA</div>
        <div class="api-grid" id="sorguGrid"></div>
    </div>

    <div class="security-badge">
        🔒 XSS Koruması | 🛡️ Rate Limiting (10/dk) | 🌐 SSL | 🚫 DDoS Koruması
    </div>

    <script>
        // NABI API Listesi - TÜM PARAMETRELER DOLU
        const nabiApis = [
            { name: "Ad Soyad Sorgula", category: "NABI", desc: "İsim ve soyisim ile kişi sorgulama", endpoint: "/api/adsoyad", params: ["adi", "soyadi"], baseUrl: "https://api.nabi.com.gov.2026tr.xyz", examples: {adi: "eymen", soyadi: "yavuz"} },
            { name: "Sulale Sorgula", category: "NABI", desc: "Tüm aile bireylerini sorgulama", endpoint: "/api/sulale", params: ["tc"], baseUrl: "https://api.nabi.com.gov.2026tr.xyz", examples: {tc: "11111111110"} },
            { name: "Çocuklar Sorgula", category: "NABI", desc: "Kişinin çocuklarını sorgulama", endpoint: "/api/cocuklar", params: ["tc"], baseUrl: "https://api.nabi.com.gov.2026tr.xyz", examples: {tc: "11111111110"} },
            { name: "Kardeşler Sorgula", category: "NABI", desc: "Kişinin kardeşlerini sorgulama", endpoint: "/api/kardesler", params: ["tc"], baseUrl: "https://api.nabi.com.gov.2026tr.xyz", examples: {tc: "11111111110"} },
            { name: "Anne Bilgisi", category: "NABI", desc: "Kişinin anne bilgileri", endpoint: "/api/anne", params: ["tc"], baseUrl: "https://api.nabi.com.gov.2026tr.xyz", examples: {tc: "11111111110"} },
            { name: "Baba Bilgisi", category: "NABI", desc: "Kişinin baba bilgileri", endpoint: "/api/baba", params: ["tc"], baseUrl: "https://api.nabi.com.gov.2026tr.xyz", examples: {tc: "11111111110"} },
            { name: "Eş Bilgisi", category: "NABI", desc: "Kişinin eş bilgileri", endpoint: "/api/es", params: ["tc"], baseUrl: "https://api.nabi.com.gov.2026tr.xyz", examples: {tc: "11111111110"} },
            { name: "Anne Adres", category: "NABI", desc: "Annenin adres bilgisi", endpoint: "/api/anneadres", params: ["tc"], baseUrl: "https://api.nabi.com.gov.2026tr.xyz", examples: {tc: "11111111110"} },
            { name: "Baba Adres", category: "NABI", desc: "Babanın adres bilgisi", endpoint: "/api/babaadres", params: ["tc"], baseUrl: "https://api.nabi.com.gov.2026tr.xyz", examples: {tc: "11111111110"} },
            { name: "Adres Sorgula", category: "NABI", desc: "Kişinin adres bilgisi", endpoint: "/api/adres", params: ["tc"], baseUrl: "https://api.nabi.com.gov.2026tr.xyz", examples: {tc: "11111111110"} }
        ];

        // Kapsamlı API Listesi - TÜM PARAMETRELER DOLU
        const sorguApis = [
            { name: "Sicil Sorgula", category: "ITO", desc: "İTO sicil numarası ile firma sorgulama", endpoint: "/api/sicil-sorgula", params: ["sicil"], baseUrl: "https://sizin-app-name.onrender.com", pathParam: true, examples: {sicil: "340"} },
            { name: "Plaka Ceza Sorgula", category: "TRAFİK", desc: "Plaka ile ceza sorgulama", endpoint: "/api/plaka-ceza-sorgula", params: ["plaka"], baseUrl: "https://sizin-app-name.onrender.com", examples: {plaka: "34APP328"} },
            { name: "Hak Sahipliği", category: "DANIŞTAY", desc: "TC ile hak sahipliği sorgulama", endpoint: "/api/hak-sahipligi-sorgula", params: ["tc"], baseUrl: "https://sizin-app-name.onrender.com", pathParam: true, examples: {tc: "11111111110"} },
            { name: "Sinav Türleri", category: "EĞİTİM", desc: "Sınav türleri listesi", endpoint: "/api/sinav-turleri", params: [], baseUrl: "https://sizin-app-name.onrender.com", examples: {} },
            { name: "Sınav Sonucu", category: "EĞİTİM", desc: "TC ile sınav sonucu sorgulama", endpoint: "/api/sinav-sonuc-sorgula", params: ["tc", "tur"], baseUrl: "https://sizin-app-name.onrender.com", examples: {tc: "11111111110", tur: "tyt"} },
            { name: "GİG Hak Sahipliği", category: "MÜZİK", desc: "Ad, soyad ve doğum tarihi ile sorgulama", endpoint: "/api/gig-hak-sahipligi-sorgula", params: ["ad", "soyad", "dt"], baseUrl: "https://sizin-app-name.onrender.com", examples: {ad: "ROKET", soyad: "ATAR", dt: "16/03/1998"} },
            { name: "Avukat İstanbul", category: "BARO", desc: "İstanbul Barosu avukat sorgulama", endpoint: "/api/avukat-sorgula-istanbul", params: ["sicil"], baseUrl: "https://sizin-app-name.onrender.com", examples: {sicil: "340"} },
            { name: "Avukat Ankara", category: "BARO", desc: "Ankara Barosu avukat sorgulama", endpoint: "/api/avukat-sorgula-ankara", params: ["ad", "soyad"], baseUrl: "https://sizin-app-name.onrender.com", examples: {ad: "Mehmet", soyad: "Yilmaz"} },
            { name: "Uçuş Durumu", category: "THY", desc: "THY uçuş durumu sorgulama", endpoint: "/api/ucus-durumu", params: ["no", "tarih"], baseUrl: "https://sizin-app-name.onrender.com", examples: {no: "1987", tarih: "2026-05-22"} },
            { name: "Hakem Ara", category: "TFF", desc: "TFF hakem sorgulama", endpoint: "/api/hakem-ara", params: ["ad", "soyad"], baseUrl: "https://sizin-app-name.onrender.com", examples: {ad: "Ali", soyad: "Demir"} },
            { name: "Enerji Borç", category: "MEPA", desc: "Enerji faturası borç sorgulama", endpoint: "/api/enerji-fatura-borc-sorgula", params: ["tesisat"], baseUrl: "https://sizin-app-name.onrender.com", examples: {tesisat: "1001234567"} },
            { name: "Araç Bilgisi", category: "ARAÇ", desc: "Plaka ile araç bilgisi sorgulama", endpoint: "/api/arac-bilgisi", params: ["plaka"], baseUrl: "https://sizin-app-name.onrender.com", examples: {plaka: "34ABC345"} }
        ];

        function buildUrl(baseUrl, endpoint, params, values, pathParam = false) {
            if (pathParam && params.length > 0 && values[params[0]]) {
                return `${baseUrl}${endpoint}/${values[params[0]]}`;
            }
            const urlParams = new URLSearchParams();
            params.forEach(param => {
                if (values[param]) {
                    urlParams.append(param, values[param]);
                }
            });
            const queryString = urlParams.toString();
            return `${baseUrl}${endpoint}${queryString ? '?' + queryString : ''}`;
        }

        function createNabiCard(api, index) {
            const card = document.createElement('div');
            card.className = 'nabi-card';
            
            const fullUrl = `${api.baseUrl}${api.endpoint}`;
            
            card.innerHTML = `
                <div class="card-header">
                    <span class="api-name">${api.name}</span>
                    <span class="api-category">${api.category}</span>
                </div>
                <div class="api-description">${api.desc}</div>
                <div class="api-url" id="url-n-${index}">${fullUrl}</div>
                <div class="button-group">
                    <button class="btn-copy" onclick="copyToClipboard('${fullUrl}')">📋 Kopyala</button>
                    <button class="btn-open" onclick="openInNewTab('${fullUrl}')">🔗 Aç</button>
                    <button class="btn-param" onclick="toggleParams('n', ${index})">⚙️ Parametre</button>
                </div>
                <div class="param-input" id="params-n-${index}">
                    ${api.params.map(param => `
                        <div class="param-group">
                            <label>${param.toUpperCase()}:</label>
                            <input type="text" id="param-${param}-n-${index}" placeholder="${api.examples[param] || 'Değer girin'}" value="${api.examples[param] || ''}">
                        </div>
                    `).join('')}
                    <button class="btn-test" onclick="testApi('n', ${index}, '${api.endpoint}', ${JSON.stringify(api.params)}, '${api.baseUrl}', false, ${JSON.stringify(api.examples)})">
                        🚀 Test Et
                    </button>
                    <div class="result-area" id="result-n-${index}">
                        <pre>Sonuç burada görünecek...</pre>
                    </div>
                </div>
            `;
            return card;
        }

        function createSorguCard(api, index) {
            const card = document.createElement('div');
            card.className = 'sorgu-card';
            
            const fullUrl = `${api.baseUrl}${api.endpoint}`;
            
            card.innerHTML = `
                <div class="card-header">
                    <span class="api-name">${api.name}</span>
                    <span class="api-category">${api.category}</span>
                </div>
                <div class="api-description">${api.desc}</div>
                <div class="api-url" id="url-s-${index}">${fullUrl}</div>
                <div class="button-group">
                    <button class="btn-copy" onclick="copyToClipboard('${fullUrl}')">📋 Kopyala</button>
                    <button class="btn-open" onclick="openInNewTab('${fullUrl}')">🔗 Aç</button>
                    <button class="btn-param" onclick="toggleParams('s', ${index})">⚙️ Parametre</button>
                </div>
                <div class="param-input" id="params-s-${index}">
                    ${api.params.map(param => `
                        <div class="param-group">
                            <label>${param.toUpperCase()}:</label>
                            <input type="text" id="param-${param}-s-${index}" placeholder="${api.examples[param] || 'Değer girin'}" value="${api.examples[param] || ''}">
                        </div>
                    `).join('')}
                    <button class="btn-test" onclick="testApi('s', ${index}, '${api.endpoint}', ${JSON.stringify(api.params)}, '${api.baseUrl}', ${api.pathParam || false}, ${JSON.stringify(api.examples)})">
                        🚀 Test Et
                    </button>
                    <div class="result-area" id="result-s-${index}">
                        <pre>Sonuç burada görünecek...</pre>
                    </div>
                </div>
            `;
            return card;
        }

        function toggleParams(type, index) {
            const paramsDiv = document.getElementById(`params-${type}-${index}`);
            paramsDiv.classList.toggle('active');
        }

        async function testApi(type, index, endpoint, params, baseUrl, pathParam, examples) {
            const values = {};
            for (const param of params) {
                const input = document.getElementById(`param-${param}-${type}-${index}`);
                if (input && input.value) {
                    values[param] = input.value;
                } else if (examples[param]) {
                    values[param] = examples[param];
                }
            }
            
            const missingParams = params.filter(p => !values[p]);
            if (missingParams.length > 0) {
                alert(`Eksik parametre: ${missingParams.join(', ')}`);
                return;
            }
            
            const url = buildUrl(baseUrl, endpoint, params, values, pathParam);
            const resultDiv = document.getElementById(`result-${type}-${index}`);
            const pre = resultDiv.querySelector('pre');
            
            resultDiv.classList.add('active');
            pre.textContent = 'Yükleniyor...';
            
            try {
                const response = await fetch(url);
                const data = await response.json();
                pre.textContent = JSON.stringify(data, null, 2);
            } catch (error) {
                pre.textContent = `Hata: ${error.message}`;
            }
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
                font-style: italic;
                animation: fadeOut 2s forwards;
            `;
            document.body.appendChild(notification);
            setTimeout(() => notification.remove(), 2000);
        }

        const nabiGrid = document.getElementById('nabiGrid');
        const sorguGrid = document.getElementById('sorguGrid');
        
        nabiApis.forEach((api, index) => {
            nabiGrid.appendChild(createNabiCard(api, index));
        });
        
        sorguApis.forEach((api, index) => {
            sorguGrid.appendChild(createSorguCard(api, index));
        });
        
        document.getElementById('totalApis').textContent = nabiApis.length + sorguApis.length;
    </script>
</body>
</html>
"""

@app.route('/')
@limiter.limit("30 per minute")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/nabi/<endpoint>')
@limiter.limit("10 per minute")
def nabi_proxy(endpoint):
    tc = request.args.get('tc')
    adi = request.args.get('adi')
    soyadi = request.args.get('soyadi')
    
    params = {}
    if tc:
        params['tc'] = tc
    if adi:
        params['adi'] = adi
    if soyadi:
        params['soyadi'] = soyadi
    
    result = nabi.sorgula(endpoint, **params)
    return jsonify(xss_clean(result))

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "security": "active",
        "domain": "api.nabiservices.com.gov.2026tr.xyz"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
