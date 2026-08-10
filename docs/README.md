# Socrapper - General Internet Sentiment Scraper

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Status](https://img.shields.io/badge/status-production%20ready-green)
![License](https://img.shields.io/badge/license-MIT-green)

Web scraping dan analisis sentimen dari internet secara general menggunakan **Django 4.2** + **Scrapling** dan **React 18** frontend.

Scrape keseluruhan internet — bukan hanya beberapa platform. User bisa filter platform tertentu atau biarkan scraper mencari di seluruh web.

## Features

### General Internet Scraping
- **Scrapling** engine dengan anti-bot bypass (StealthyFetcher)
- Scrape URL apapun di internet, bukan hanya platform tertentu
- 9 platform selector opsional: Twitter, Reddit, News, StackOverflow, GitHub, YouTube, Instagram, TikTok, Facebook
- Fallback ke Google Search umum jika tidak ada platform dipilih

### Sentiment Analysis
- Keyword-based dengan **negation handling** (window 3 kata)
- 16 positive + 18 negative keywords (Indonesian + English)
- Multi-word phrase matching
- Contoh: "tidak bagus" → **negative** (bukan positive)

### Internet Surfer
- **Quick Surf**: Pencarian cepat tanpa extract content
- **Full Surf**: Search + extract + analisis sentimen
- **Deep Surf**: Multiple queries + full extraction + detailed analysis
- **AI Analyze**: LLM-powered analysis (OpenAI-compatible API)

### Analytics Dashboard
- Doughnut chart sentimen (Chart.js)
- Bar charts engagement statistics
- History scraping dengan pagination
- Export data ke CSV

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2 + Django REST Framework |
| Scraping | Scrapling (StealthyFetcher + Fetcher) |
| Database | Supabase PostgreSQL (or SQLite for dev) |
| Frontend | React 18 + Vite 4 |
| Charts | Chart.js + react-chartjs-2 |
| LLM | OpenAI-compatible API (mimo-v2.5-pro) |

## Project Structure

```
Socrapper/
├── .github/workflows/             # CI/CD (GitHub Actions)
│   └── deploy.yml                 #   test + lint → deploy VPS
├── config/                        # Tool konfigurasi
│   ├── pytest.ini                 #   pytest (env DB, settings)
│   └── ruff.toml                  #   ruff linter + formatter
├── docs/                          # Dokumentasi
│   ├── AGENTS.md                  #   Panduan AI agent
│   ├── BUG_REPORT.md              #   Bug tracker
│   └── README.md                  #   Dokumentasi utama
├── manage.py                      # Django CLI
├── requirements.txt               # Python runtime dependencies
├── requirements-dev.txt           # Python dev/test dependencies
├── package.json                   # Node dependencies
├── vite.config.js                 # Vite → proxy ke Django:8000
├── index.html                     # React SPA entry
├── .env                           # Environment config
├── .gitignore
├── README.md                      # Root redirect → docs/README.md
│
├── socrapper/                     # Django project config
│   ├── middleware.py              #   Request logging middleware
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── scraper/                       # App: scraping
│   ├── models.py                  #   ScrapeHistory model
│   ├── views.py                   #   9 API endpoints
│   ├── urls.py
│   ├── migrations/
│   └── services/
│       ├── sentiment_service.py   #   Keyword + negation + LLM
│       ├── csv_export_service.py  #   CSV export
│       ├── news_cache_service.py  #   News pre-fetch cache
│       ├── web_scraper_service.py #   Scrapling engine
│       ├── cache_utils.py         #   TTLCache
│       ├── rate_limiter.py        #   Domain rate limiting
│       ├── retry_utils.py         #   Retry helper
│       └── shared_client.py       #   Shared httpx client
│
├── surfer/                        # App: internet surfer
│   ├── views.py                   #   5 API endpoints
│   ├── urls.py
│   └── services/
│       ├── search_engine_service.py      # Google News + Web
│       ├── content_extractor_service.py  # Article extraction
│       ├── llm_analysis_service.py       # LLM (OpenAI-compat)
│       └── internet_surfer_service.py    # Orchestrator
│
├── resources/js/                  # React frontend
│   ├── app.jsx                    # Entry point
│   ├── css/newspaper.css
│   ├── pages/App.jsx              # Root component
│   └── components/
│       ├── common/                #   Reusable UI
│       │   ├── ErrorBoundary.jsx
│       │   ├── LoadingIndicator.jsx
│       │   └── SocrapperLoader.jsx
│       ├── layout/                #   Tata letak
│       │   ├── AiAnalysisCard.jsx
│       │   ├── HomeContent.jsx
│       │   ├── HomeSidebar.jsx
│       │   └── InputSection.jsx
│       └── tabs/                  #   Panel konten
│           ├── HistoryTab.jsx
│           ├── RawDataTab.jsx
│           ├── SentimentTab.jsx
│           ├── StatisticsTab.jsx
│           └── SurfResultsTab.jsx
│
└── tests/                         # Pytest test suite (149 tests)
    ├── conftest.py
    ├── settings_test.py
    ├── test_api_endpoints.py
    ├── test_cache_and_rate_limiter.py
    ├── test_middleware.py
    ├── test_search_engine_service.py
    ├── test_sentiment_service.py
    └── test_web_scraper_service.py
```

## Requirements

- Python 3.10+
- Node.js 16+ dan npm
- Modern browser (Chrome, Firefox, Safari, Edge)

## Installation

### 1. Clone repository

```bash
git clone https://github.com/GipsyDanger-dev/Socrapper.git
cd Socrapper
```

### 2. Setup Python backend

```bash
# Install Python dependencies
pip install -r requirements.txt

# Copy dan edit environment config
cp .env.example .env  # atau buat .env manual (lihat Environment Variables)

# Jalankan database migrations
python manage.py migrate
```

### 3. Setup React frontend

```bash
# Install Node dependencies
npm install
```

### 4. (Opsional) Jalankan test suite & linter

```bash
# Install dev/test dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Jalankan seluruh test
python -m pytest -c config/pytest.ini tests/

# Jalankan linter (konfigurasi di config/ruff.toml)
ruff --config config/ruff.toml check .

# Format kode otomatis (dan cek tanpa mengubah file)
ruff --config config/ruff.toml format .
ruff --config config/ruff.toml format --check .
```

### 5. Jalankan aplikasi

**Terminal 1 — Django backend:**
```bash
python manage.py runserver 8000
```

**Terminal 2 — Vite dev server:**
```bash
npm run dev
```

Buka **http://localhost:5173** di browser.

## Environment Variables

Buat file `.env` di root project:

```env
# Database: sqlite / mysql / postgresql
DB_ENGINE=sqlite

# Untuk PostgreSQL (Supabase)
# DB_ENGINE=postgresql
# DB_HOST=db.xxxxx.supabase.co
# DB_PORT=5432
# DB_DATABASE=postgres
# DB_USERNAME=postgres
# DB_PASSWORD=your-password

# LLM Configuration (opsional, untuk AI analysis)
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://openrouter.ai/api/v1
# Bisa berupa rantai fallback (dipisah koma) — model berikutnya dicoba jika yang pertama gagal/rate-limited.
# `openrouter/free` di akhir adalah router otomatis yang memilih model gratis apa pun yang tersedia.
LLM_MODEL=google/gemma-4-31b-it:free,openai/gpt-oss-20b:free,nvidia/nemotron-3-super-120b-a12b:free,google/gemma-4-26b-a4b-it:free,nvidia/nemotron-3-ultra-550b-a55b:free,nvidia/nemotron-3-nano-30b-a3b:free,inclusionai/ling-3.0-flash:free,openrouter/free

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### Database Options

| Engine | Config |
|--------|--------|
| SQLite (default) | `DB_ENGINE=sqlite` — zero config, file-based |
| PostgreSQL | `DB_ENGINE=postgresql` + host/port/user/pass |
| MySQL | `DB_ENGINE=mysql` + host/port/user/pass |

### LLM Configuration (Optional)

LLM digunakan untuk analisis sentimen (AI) dan fitur **AI Analyze** di Internet Surfer. Tanpa LLM, fitur ini tetap jalan dengan fallback keyword-based analysis.

Supported API:
- OpenAI API (`https://api.openai.com/v1`)
- OpenRouter (`https://openrouter.ai/api/v1`) — termasuk model gratis berakhiran `:free`
- Any OpenAI-compatible API (LocalAI, Ollama, etc)

`LLM_MODEL` bisa berupa rantai fallback yang dipisah koma. Jika model pertama gagal atau kena rate-limit (umum terjadi pada model gratis), model berikutnya akan dicoba otomatis sampai ada yang berhasil. Setiap request punya timeout 60 detik, jadi model yang hang tidak akan menghentikan rantai.

**Tips:** simpan `openrouter/free` sebagai model terakhir — ini router dinamis OpenRouter yang otomatis memilih model gratis apa pun yang tersedia, jadi AI analysis hampir tidak pernah jatuh ke keyword-based fallback. Rantai model gratis bisa berubah sewaktu-waktu (model sering di-retire); perbarui daftar ini sesuai model `:free` aktif di https://openrouter.ai/models.

## API Endpoints

### Scraper

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/platforms` | Daftar platform yang didukung |
| `POST` | `/api/scrape` | Mulai scraping |
| `POST` | `/api/analyze` | Analisis sentimen teks |
| `GET` | `/api/scrape-history` | History scraping (paginated) |
| `DELETE` | `/api/scrape-history/<id>` | Hapus history |

### Export

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/export` | Export data ke CSV |
| `GET` | `/api/exports` | List file export |
| `GET` | `/api/exports/<file>/download` | Download file export |
| `DELETE` | `/api/exports/<file>` | Hapus file export |

### Internet Surfer

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/surf` | Full surf (search + extract + analyze) |
| `POST` | `/api/surf/quick` | Quick search tanpa extract |
| `POST` | `/api/surf/deep` | Deep surf (multiple queries) |
| `POST` | `/api/surf/extract` | Extract content dari URL |
| `POST` | `/api/surf/ai-analyze` | AI-powered analysis |

### Example: Scrape

```bash
curl -X POST http://localhost:8000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"platform":"reddit","keyword":"python","limit":5}'
```

### Example: Analyze Sentiment

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"texts":["bagus sekali","tidak bagus","biasa saja"]}'
```

### Example: Quick Surf

```bash
curl -X POST http://localhost:8000/api/surf/quick \
  -H "Content-Type: application/json" \
  -d '{"query":"AI news","limit":5}'
```

## How It Works

### Scraping Flow

```
User Input (keyword + optional platform)
        ↓
WebScraperService
        ↓
Platform URL builder / Google Search
        ↓
Scrapling StealthyFetcher (anti-bot bypass)
        ↓
HTML parsing → extract results
        ↓
Fallback data jika scraping gagal
        ↓
Sentiment analysis → save to history
        ↓
JSON response ke frontend
```

### Sentiment Analysis

Analisis berbasis keyword dengan negation handling:

```python
# "bagus" → positive
# "tidak bagus" → negative (negation detected)
# "sangat tidak bagus" → negative (3-word window)
# "biasa saja" → neutral
```

Negation window: 3 kata sebelum keyword. Mendeteksi: tidak, bukan, kurang, jangan, belum, ga, gak, nggak, enggak, tanpa.

### Internet Surfer

```
Query → Google News RSS + Google Web Search
        ↓
URL extraction (parallel, max 5 concurrent)
        ↓
Content extraction (title, author, date, images)
        ↓
Merge search + extracted content
        ↓
Sentiment analysis on all content
        ↓
Summary generation (key topics, sources)
```

## Troubleshooting

### Server tidak mau start

```bash
# Pastikan port 8000 tidak dipakai
netstat -ano | findstr :8000

# Atau pakai port lain
python manage.py runserver 8001
```

### Database connection error

```bash
# Cek .env configuration
# Untuk development, pakai SQLite:
DB_ENGINE=sqlite
```

### Scrapling import error

```bash
# Install/reinstall scrapling
pip install --upgrade scrapling
```

### CORS error di browser

Pastikan `django-cors-headers` terinstall dan `CORS_ALLOW_ALL_ORIGINS = True` di settings.py.

## Contributing

1. Fork repository
2. Buat feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push ke branch (`git push origin feature/amazing-feature`)
5. Buka Pull Request

## License

MIT License

---

**Django + Scrapling + React — Scrape the entire internet.**

