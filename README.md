# Socrapper - Social Media Sentiment Scraper

Website scraping dan analisis sentimen dari berbagai platform media sosial menggunakan **Laravel** dan **React JS**.

## 📁 Struktur Folder

```
Socrapper/
│
├── app/
│   ├── Http/
│   │   └── Controllers/
│   │       └── ScraperController.php
│   ├── Services/
│   │   ├── ScraperService.php
│   │   └── SentimentAnalysisService.php
│   └── Models/
│
├── routes/
│   ├── api.php               # API Routes
│   └── web.php               # Web Routes
│
├── resources/
│   ├── views/
│   │   └── app.blade.php     # Blade template untuk React
│   └── js/
│       ├── app.jsx           # React entry point
│       ├── pages/
│       │   └── App.jsx       # Main React component
│       ├── components/       # React components
│       │   ├── InputSection.jsx
│       │   ├── RawDataTab.jsx
│       │   ├── SentimentTab.jsx
│       │   ├── StatisticsTab.jsx
│       │   └── LoadingIndicator.jsx
│       └── css/
│           └── app.css       # Styling
│
├── database/
│   └── migrations/           # Database migrations
│
├── composer.json             # PHP dependencies
├── package.json              # Node dependencies
├── vite.config.js            # Vite configuration
├── .env.example              # Environment variables example
└── README.md                 # This file
```

## 🚀 Fitur Utama

- **Multi-Platform Scraping**: Twitter/X, Instagram, TikTok, Facebook, Reddit, YouTube
- **Sentiment Analysis**: Analisis sentimen otomatis (Positif/Negatif/Netral)
- **Real-time Statistics**: Engagement metrics (likes, comments, shares)
- **Modern UI**: React JS dengan styling responsif
- **RESTful API**: Backend Laravel dengan endpoints yang clean
- **Export Data**: Fitur export JSON/CSV (bonus)

## 📋 Requirements

- PHP 8.1+
- Node.js 16+ dan npm
- Composer
- MySQL (optional, untuk production)
- Modern browser (Chrome, Firefox, Safari, Edge)

## 🔧 Instalasi & Setup

### 1. Clone Repository
```bash
git clone <repo-url>
cd Socrapper
```

### 2. Setup Backend (Laravel)
```bash
# Copy environment file
cp .env.example .env

# Install PHP dependencies
composer install

# Generate application key
php artisan key:generate

# (Optional) Setup database
php artisan migrate
```

### 3. Setup Frontend (React + Node)
```bash
# Install Node dependencies
npm install

# Build assets
npm run build

# Atau untuk development dengan hot reload
npm run dev
```

### 4. Jalankan Aplikasi

**Option 1: Menggunakan Laravel Artisan**
```bash
php artisan serve
```
Akses: `http://localhost:8000`

**Option 2: Menggunakan Node.js (untuk development)**
```bash
# Terminal 1: Build assets dengan hot reload
npm run dev

# Terminal 2: Jalankan Laravel server
php artisan serve
```

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

### POST `/api/scrape`
Memulai proses scraping

**Request:**
```json
{
  "platform": "twitter",
  "keyword": "python",
  "limit": 50
}
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "platform": "twitter",
      "author": "User 1",
      "text": "Postingan tentang python",
      "timestamp": "2024-05-09T10:30:00Z",
      "likes": 10,
      "comments": 5,
      "shares": 2,
      "url": "https://twitter.com/post/1"
    }
  ],
  "total": 50,
  "platform": "twitter",
  "keyword": "python"
}
```

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
    "positive": 1,
    "negative": 1,
    "neutral": 1,
    "percentage": {
      "positive": 33.33,
      "negative": 33.33,
      "neutral": 33.34
    },
    "details": [
      {
        "text": "Produk ini sangat bagus dan memuaskan!",
        "sentiment": "positive",
        "confidence": 30
      },
      ...
    ]
  }
}
```

## 🔐 Konfigurasi API Keys

Buat file `.env` dan tambahkan API keys berikut:

### Twitter/X
```
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret
```

### Instagram
```
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
```

### Reddit
```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=your_user_agent
```

### YouTube
```
YOUTUBE_API_KEY=your_api_key
```

### TikTok & Facebook
```
TIKTOK_API_KEY=your_api_key
FACEBOOK_API_KEY=your_api_key
```

## 📝 Cara Menggunakan

1. **Pilih Platform**: Pilih media sosial dari dropdown
2. **Masukkan Keyword**: Ketikkan keyword atau hashtag yang ingin dicari
3. **Tentukan Limit**: Tentukan jumlah data yang ingin diambil (1-1000)
4. **Klik Scraping**: Tekan tombol "Mulai Scraping"
5. **Lihat Hasil**: 
   - Tab "Data Mentah": Tampilkan raw data yang di-scrape
   - Tab "Analisis Sentimen": Lihat hasil sentiment analysis dengan percentage
   - Tab "Statistik": Lihat engagement statistics (likes, comments, shares)

## 🏗️ Architecture

### Backend (Laravel)
- **ScraperController**: Handle API requests untuk scraping
- **ScraperService**: Logic untuk scraping dari berbagai platform
- **SentimentAnalysisService**: Logic untuk analisis sentimen
- **Routes**: RESTful API endpoints

### Frontend (React)
- **App Component**: Main component yang manage state
- **InputSection**: Form untuk input parameter scraping
- **RawDataTab**: Tampilkan raw data dari scraping
- **SentimentTab**: Tampilkan hasil sentiment analysis
- **StatisticsTab**: Tampilkan statistik engagement
- **LoadingIndicator**: Loading state indicator

## 🚧 TODO/Fitur Masa Depan

- [ ] Implementasi scraping real dari API masing-masing platform
- [ ] Advanced sentiment analysis dengan Machine Learning (TensorFlow.js)
- [ ] Database untuk menyimpan scraping history
- [ ] User authentication & authorization
- [ ] Real-time scraping dengan WebSocket
- [ ] Data visualization (charts, graphs) dengan Chart.js
- [ ] Scheduled scraping tasks dengan Laravel Task Scheduler
- [ ] Notification system (email, push notification)
- [ ] Export ke Excel format
- [ ] Trending analysis
- [ ] Comparison tool antar platform

## ⚠️ Catatan Penting

- **Terms of Service**: Selalu perhatikan Terms of Service dari setiap platform
- **Rate Limiting**: Jangan melakukan scraping berlebihan yang bisa trigger rate limiting
- **API Keys**: Simpan API keys dengan aman di file `.env`, jangan commit ke repository
- **Privacy**: Perhatikan regulasi tentang data collection dan privacy (GDPR, dll)
- **Ethical Scraping**: Lakukan scraping dengan etis dan bertanggung jawab

## 🤝 Kontribusi

Silakan membuat pull request untuk improvements atau bug fixes.

## 📄 Lisensi

MIT License - Silakan gunakan untuk keperluan personal maupun komersial.

## 📧 Kontak

Untuk pertanyaan atau masalah, silakan buka issue di repository ini.

---

**Dibuat dengan ❤️ untuk analisis sentiment media sosial yang lebih baik!**
