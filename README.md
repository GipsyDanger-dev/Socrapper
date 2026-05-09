# Socrapper - Social Media Sentiment Scraper

![Version](https://img.shields.io/badge/version-1.1.0-blue)
![Status](https://img.shields.io/badge/status-production%20ready-green)
![License](https://img.shields.io/badge/license-MIT-green)

Website scraping dan analisis sentimen dari berbagai platform media sosial menggunakan **Laravel 10** dan **React 18 JS** dengan **Real API Integration**.

**A modern full-stack application for scraping and analyzing social media sentiment across 6 platforms with real API integration.**

## 🌟 Features

### ✅ Real API Integration (v1.1.0)
- **Twitter API v2** - Real-time tweet search with public metrics
- **Instagram Graph API** - Business account media and engagement
- **TikTok API** - Video search and creator analytics
- **Facebook Graph API** - Page posts and engagement data
- **Reddit API** - Post search and subreddit data
- **YouTube Data API v3** - Video search and statistics

### 📊 Sentiment Analysis
- Keyword-based sentiment detection (Positive/Negative/Neutral)
- Confidence scoring for each classification
- Multi-language support (Indonesian/English)
- Aggregated sentiment statistics

### 📈 Analytics Dashboard
- Real-time engagement metrics
- Platform-specific statistics
- Comparative analysis across platforms
- Responsive UI design

### 🔄 Automatic Fallback
- Graceful fallback to realistic simulated data when APIs unavailable
- Perfect for development and testing
- Maintains consistent data structure

## 📁 Struktur Folder

```
Socrapper/
├── app/
│   ├── Http/
│   │   ├── Controllers/
│   │   │   └── ScraperController.php      # API endpoints
│   │   └── Middleware/                    # HTTP middleware
│   └── Services/
│       ├── ScraperService.php             # Main orchestrator
│       ├── SentimentAnalysisService.php   # Sentiment detection
│       └── Platforms/                     # Platform-specific APIs ⭐ NEW
│           ├── BasePlatformAPI.php        # Abstract base class
│           ├── TwitterAPI.php
│           ├── InstagramAPI.php
│           ├── TikTokAPI.php
│           ├── FacebookAPI.php
│           ├── RedditAPI.php
│           └── YouTubeAPI.php
├── routes/
│   ├── api.php               # API Routes
│   └── web.php               # Web Routes
├── resources/
│   ├── views/
│   │   └── app.blade.php     # Blade template untuk React
│   ├── js/
│   │   ├── app.jsx           # React entry point
│   │   ├── pages/
│   │   │   └── App.jsx       # Main React component
│   │   ├── components/       # React components
│   │   │   ├── InputSection.jsx
│   │   │   ├── RawDataTab.jsx
│   │   │   ├── SentimentTab.jsx
│   │   │   ├── StatisticsTab.jsx
│   │   │   └── LoadingIndicator.jsx
│   │   └── css/
│   │       └── app.css       # Styling
│   └── views/
│       └── app.blade.php
├── public/
│   ├── build/                # Compiled assets
│   └── index.php             # Entry point
├── config/
│   ├── app.php
│   ├── database.php
│   ├── auth.php
│   ├── session.php
│   ├── cache.php
│   └── view.php
├── storage/
│   └── logs/                 # Application logs
├── bootstrap/
│   ├── app.php
│   └── cache/
├── composer.json             # PHP dependencies
├── package.json              # Node dependencies
├── vite.config.js            # Vite configuration
├── .env.example              # Environment variables example
├── API_SETUP.md              # 📖 API setup guide (NEW)
├── TESTING_GUIDE.md          # 📖 Testing guide (NEW)
├── DEVELOPER_GUIDE.md        # 📖 Developer guide (NEW)
├── REAL_API_CHANGELOG.md     # 📖 Changelog (NEW)
└── README.md
```

## 🚀 Fitur Utama

- **Multi-Platform Scraping**: Twitter/X, Instagram, TikTok, Facebook, Reddit, YouTube dengan Real API Integration
- **Real API Integration** ⭐ NEW: Implementasi lengkap 6 platform API dengan fallback data otomatis
- **Sentiment Analysis**: Analisis sentimen otomatis (Positif/Negatif/Netral) dengan confidence score
- **Real-time Statistics**: Engagement metrics (likes, comments, shares) per platform
- **Modern UI**: React 18 JS dengan Vite build tool dan styling responsif
- **RESTful API**: Backend Laravel 10 dengan endpoints yang clean dan terstruktur
- **Graceful Fallback**: Realistic simulated data ketika API key tidak dikonfigurasi (perfect for development)
- **Comprehensive Documentation**: 4 panduan lengkap (API Setup, Testing, Developer, Changelog)

## 📋 Requirements

- PHP 8.1+
- Node.js 16+ dan npm
- Composer
- MySQL (optional, untuk production) atau SQLite (default)
- Modern browser (Chrome, Firefox, Safari, Edge)

## 🔧 Instalasi & Setup

### 1. Setup Backend (Laravel)
```bash
# Navigate to project directory
cd d:\Advanced\xamp\htdocs\Socrapper

# Install PHP dependencies
composer install

# Generate application key (if not already generated)
php artisan key:generate
```

### 2. Setup Frontend (React + Node)
```bash
# Install Node dependencies
npm install

# Build assets untuk production
npm run build

# Atau untuk development dengan hot reload
npm run dev
```

### 3. Jalankan Aplikasi

**Best Practice: Start Both Servers**

Terminal 1 - Laravel Backend:
```bash
php artisan serve
```
Runs on: `http://localhost:8000`

Terminal 2 - Frontend Development (optional for dev):
```bash
npm run dev
```
Runs on: `http://localhost:5173` (but loads from Laravel)

**Access Application:**
```
http://localhost:8000
```

## 📚 Documentation

### 📖 Main Guides

| Guide | Purpose |
|-------|---------|
| [**API_SETUP.md**](API_SETUP.md) | Configure real API credentials untuk setiap platform |
| [**TESTING_GUIDE.md**](TESTING_GUIDE.md) | How to test all features tanpa API keys atau dengan real credentials |
| [**DEVELOPER_GUIDE.md**](DEVELOPER_GUIDE.md) | Architecture & how to add new platforms |
| [**REAL_API_CHANGELOG.md**](REAL_API_CHANGELOG.md) | Implementation details & v1.1.0 updates |

**Baca dokumentasi ini setelah instalasi!**

## 🎯 Quick Start Usage

### Test Without API Keys (Fallback Mode) ✅
```
1. Buka http://localhost:8000
2. Pilih platform (Twitter, Instagram, TikTok, Facebook, Reddit, atau YouTube)
3. Masukkan keyword (contoh: "React", "Laravel", "Technology")
4. Klik "Mulai Scraping"
5. Lihat hasil di tab Raw Data, Sentiment, Statistics

Result: 10 realistic simulated posts appear instantly
Fallback data marked with "[Fallback Data]"
Perfect untuk testing dan development
```

### Test With Real API Data 🔌
```
1. Follow API_SETUP.md untuk setiap platform
2. Add credentials ke .env file
3. Run: php artisan cache:clear && php artisan config:clear
4. Reload http://localhost:8000
5. Results sekarang show REAL data dari platforms!
```

**See [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive testing examples**

## 📚 API Endpoints

### GET `/api/platforms`
Mengembalikan daftar platform yang didukung
```json
{
  "platforms": {
    "twitter": "Twitter/X",
    "instagram": "Instagram",
    "tiktok": "TikTok",
    "facebook": "Facebook",
    "reddit": "Reddit",
    "youtube": "YouTube"
  }
}
```

### GET `/api/platforms`
Mengembalikan daftar platform yang didukung
```json
{
  "platforms": [
    "twitter",
    "instagram", 
    "tiktok",
    "facebook",
    "reddit",
    "youtube"
  ]
}
```

### POST `/api/scrape`
Memulai proses scraping dari platform pilihan

**Request:**
```json
{
  "platform": "twitter",
  "keyword": "Laravel",
  "limit": 50
}
```

**Response (with or without API keys):**
```json
{
  "success": true,
  "data": [
    {
      "id": "twit_1",
      "platform": "twitter",
      "author": "John Doe",
      "text": "Laravel is amazing!",
      "timestamp": "2026-05-09T10:30:00Z",
      "likes": 100,
      "comments": 25,
      "shares": 10,
      "url": "https://twitter.com/..."
    },
    // ... more posts
  ],
  "total": 50,
  "platform": "twitter",
  "keyword": "Laravel"
}
```

**Note:** If API keys not configured, returns realistic fallback data marked "[Fallback Data]"

### POST `/api/analyze`
Analisis sentimen dari teks

**Request:**
```json
{
  "texts": [
    "Produk ini sangat bagus dan memuaskan!",
    "Sangat kecewa dengan layanannya",
    "Produk biasa saja"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "summary": {
      "positive": 1,
      "negative": 1,
      "neutral": 1
    },
    "percentage": {
      "positive": 33.33,
      "negative": 33.33,
      "neutral": 33.34
    },
    "details": [
      {
        "text": "Produk ini sangat bagus dan memuaskan!",
        "sentiment": "positive",
        "confidence": 100
      },
      {
        "text": "Sangat kecewa dengan layanannya",
        "sentiment": "negative",
        "confidence": 100
      },
      {
        "text": "Produk biasa saja",
        "sentiment": "neutral",
        "confidence": 100
      }
    ]
  }
}
```

## 🔐 Konfigurasi - Real API Integration

### Option 1: Development Mode (No API Keys)
**Aplikasi berjalan dengan fallback data - RECOMMENDED untuk testing**

```bash
# Default .env sudah configured untuk fallback mode
# Tidak perlu setup API keys
# Jalankan aplikasi dan testing semua features

php artisan serve
# Buka http://localhost:8000
```

### Option 2: Production Mode (With Real API Keys)

Edit `.env` dan tambahkan API keys sesuai platform yang ingin digunakan:

```bash
# Twitter API v2
TWITTER_BEARER_TOKEN=AAAA...yourtoken

# Instagram Graph API
INSTAGRAM_ACCESS_TOKEN=EAA...yourtoken
INSTAGRAM_BUSINESS_ACCOUNT_ID=123456789

# TikTok API
TIKTOK_CLIENT_KEY=your_client_key
TIKTOK_CLIENT_SECRET=your_client_secret
TIKTOK_ACCESS_TOKEN=your_access_token

# Facebook Graph API
FACEBOOK_ACCESS_TOKEN=EAAC...yourtoken
FACEBOOK_PAGE_ID=1234567890

# Reddit API
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=Socrapper/1.0

# YouTube Data API v3
YOUTUBE_API_KEY=AIzaSy...yourkey
```

### Getting API Keys

**See [API_SETUP.md](API_SETUP.md) for detailed step-by-step instructions:**
- Twitter API v2 setup
- Instagram Graph API setup
- TikTok API setup
- Facebook Graph API setup  
- Reddit API setup
- YouTube Data API setup

### Applying Configuration Changes
```bash
# After adding API keys to .env
php artisan cache:clear
php artisan config:clear

# Reload application
# http://localhost:8000
```

## 📝 Cara Menggunakan

1. **Pilih Platform**: Pilih salah satu media sosial dari dropdown
   - Twitter/X
   - Instagram
   - TikTok
   - Facebook
   - Reddit
   - YouTube

2. **Masukkan Keyword**: Ketikkan keyword atau hashtag yang ingin dicari
   - Contoh: "React", "Laravel", "#technology", "#news"

3. **Tentukan Limit**: Tentukan jumlah data yang ingin diambil (1-1000)
   - Default: 50

4. **Klik "Mulai Scraping"**: Tekan tombol scraping

5. **Lihat Hasil**:
   - Tab "Data Mentah" (Raw Data): Tampilkan raw posts yang di-scrape dengan engagement metrics
   - Tab "Analisis Sentimen": Lihat hasil sentiment analysis dengan percentage breakdown
   - Tab "Statistik": Lihat engagement statistics (total & average likes, comments, shares)

## 🏗️ Architecture & Real API Integration

### Overview
Aplikasi menggunakan **Strategy Pattern** untuk platform APIs:
- Base class `BasePlatformAPI` defines interface
- Setiap platform implements `scrape()` dan `formatResponse()`
- `ScraperService` routes requests ke platform yang tepat
- Automatic fallback ke realistic simulated data

### Data Flow
```
User Input → Controller → ScraperService → Platform API
                                        ↓
                            Real Data (if configured)
                                        or
                            Fallback Data (if not)
                                        ↓
                         Standardized Format
                                        ↓
                            Frontend Display
```

### Response Format (Standardized)
```json
{
  "id": "platform_specific_id",
  "platform": "twitter",
  "author": "username",
  "text": "post content",
  "timestamp": "ISO8601",
  "likes": 100,
  "comments": 50,
  "shares": 25,
  "url": "https://..."
}
```

For more details, see [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)

## ✅ Implementation Status

### ✅ COMPLETED (v1.1.0)
- [x] Real API Integration for all 6 platforms
- [x] OAuth 2.0 and API Key authentication
- [x] Graceful fallback to simulated data
- [x] Standardized response format
- [x] Error handling and logging
- [x] Sentiment analysis service
- [x] Statistics calculation
- [x] Responsive React UI
- [x] Comprehensive documentation (API_SETUP, TESTING, DEVELOPER guides)
- [x] Production-ready codebase

### 🚧 FUTURE FEATURES
- [ ] Database persistence (scraping history)
- [ ] Machine Learning based sentiment analysis
- [ ] User authentication & authorization
- [ ] Real-time scraping with WebSocket
- [ ] Advanced data visualization (charts, graphs)
- [ ] Scheduled scraping tasks
- [ ] Email notifications
- [ ] Export to Excel/CSV format
- [ ] Trending analysis
- [ ] Platform comparison tools
- [ ] Rate limiting & request throttling
- [ ] Caching layer

## ⚠️ Important Notes

### About Real API Integration
- **Fallback Mode is Default**: Aplikasi berjalan sempurna tanpa API keys menggunakan realistic simulated data
- **API Keys are Optional**: Tambahkan credentials hanya jika ingin real data dari platforms
- **No Breaking Changes**: Fallback data ensures development tetap lancar tanpa external dependencies
- **Production Ready**: Codebase siap deploy dengan optional real API support

### Best Practices
- **Security**: Simpan API keys di `.env`, jangan commit ke repository
- **Rate Limiting**: Perhatikan rate limits setiap platform (lihat API_SETUP.md)
- **Terms of Service**: Selalu follow TOS dari setiap platform
- **Privacy**: Perhatikan regulasi data collection (GDPR, etc)
- **Ethical Scraping**: Scrape secara etis dan bertanggung jawab
- **Error Handling**: Aplikasi gracefully fallback jika API down

### Platform-Specific Notes
See [API_SETUP.md](API_SETUP.md) untuk requirements dan notes per platform:
- **Twitter**: API v2 dengan bearer token, rate limit 300/15 min
- **Instagram**: Business accounts only, rate limit 200/hour
- **TikTok**: Limited API access, use fallback untuk development
- **Facebook**: Graph API v18.0, rate limit 200/hour
- **Reddit**: OAuth 2.0 client credentials flow
- **YouTube**: API key based, rate limit 10,000 units/day

## 🐛 Troubleshooting

### Common Issues

**Dropdown platform kosong**
- Hard refresh browser (Ctrl+Shift+Delete)
- Clear browser cache
- Check `/api/platforms` endpoint returns data

**401 Unauthorized errors**
- Verify API credentials di `.env`
- Regenerate tokens dari platform dashboards
- Check token expiration

**Tidak ada data yang keluar**
- Fallback data should appear (marked "[Fallback Data]")
- Try keyword yang berbeda
- Check browser console untuk errors
- Verify platform yang dipilih

**Application tidak loading**
- Check `storage/logs/laravel.log`
- Verify both servers running (Laravel + optional Vite)
- Restart servers

See [TESTING_GUIDE.md](TESTING_GUIDE.md#troubleshooting) untuk debugging lebih detail

## 📞 Support & Documentation

### Getting Help

1. **Check Documentation First**:
   - [TESTING_GUIDE.md](TESTING_GUIDE.md) - Feature testing & examples
   - [API_SETUP.md](API_SETUP.md) - API configuration
   - [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Architecture & extending
   - [REAL_API_CHANGELOG.md](REAL_API_CHANGELOG.md) - Implementation details

2. **Review Logs**:
   ```bash
   tail -f storage/logs/laravel.log  # Check for errors
   ```

3. **Debug in Browser**:
   - Open DevTools (F12)
   - Check Network tab untuk API calls
   - Check Console untuk JavaScript errors

4. **Verify Setup**:
   - Both servers running? (`php artisan serve` + optional `npm run dev`)
   - .env configured? (tidak perlu API keys untuk development)
   - Node modules installed? (`npm install` ran successfully?)
   - PHP dependencies installed? (`composer install` ran successfully?)

## 🤝 Kontribusi

Silakan membuat pull request untuk improvements atau bug fixes:

1. Fork repository
2. Buat branch feature (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buka Pull Request

## 📄 Lisensi

MIT License - Silakan gunakan untuk keperluan personal maupun komersial.

---

## 📊 Project Stats

- **Version**: 1.1.0 (Real API Integration)
- **Last Updated**: May 9, 2026
- **Status**: ✅ Production Ready
- **Platforms Supported**: 6 (Twitter, Instagram, TikTok, Facebook, Reddit, YouTube)
- **Language**: PHP 8.1 + React 18 + JavaScript
- **Framework**: Laravel 10 + Vite 4
- **API Calls**: Real API Integration with automatic fallback

---

**Dibuat dengan ❤️ untuk analisis sentiment media sosial yang lebih baik!**

**🚀 Ready to get started?**
1. Run `php artisan serve`
2. Open http://localhost:8000
3. Read [TESTING_GUIDE.md](TESTING_GUIDE.md)
4. Start scraping!


