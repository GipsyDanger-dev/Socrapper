# Setup Guide - Laravel + React JS

## 🚀 Quick Start

### Prerequisites
Pastikan sudah install:
- PHP 8.1+ dengan extensions: BCMath, Ctype, JSON, Mbstring, OpenSSL, PDO, Tokenizer, XML
- Composer
- Node.js 16+ dan npm
- Git

### Installation Steps

#### 1. Backend Setup (Laravel)

```bash
# Install PHP dependencies
composer install

# Copy environment file
cp .env.example .env

# Generate application key
php artisan key:generate

# (Optional) Jika menggunakan database
php artisan migrate
```

#### 2. Frontend Setup (React + Vite)

```bash
# Install Node dependencies
npm install

# Untuk development (with hot reload)
npm run dev

# Untuk production build
npm run build
```

#### 3. Jalankan Server

**Terminal 1 - Start Vite Dev Server:**
```bash
npm run dev
```

**Terminal 2 - Start Laravel Server:**
```bash
php artisan serve
```

Akses aplikasi di: `http://localhost:8000`

## 📂 File Structure Penjelasan

### Backend (Laravel)

**Routes**
- `routes/api.php` - REST API endpoints
- `routes/web.php` - Web routes (blade templates)

**Controllers**
- `app/Http/Controllers/ScraperController.php` - Handle scraping requests

**Services**
- `app/Services/ScraperService.php` - Scraping logic
- `app/Services/SentimentAnalysisService.php` - Sentiment analysis logic

**Views**
- `resources/views/app.blade.php` - Main blade template (loads React app)

### Frontend (React + Vite)

**Entry Point**
- `resources/js/app.jsx` - React application entry point

**Pages**
- `resources/js/pages/App.jsx` - Main React component

**Components**
- `resources/js/components/InputSection.jsx` - Form input
- `resources/js/components/RawDataTab.jsx` - Display raw data
- `resources/js/components/SentimentTab.jsx` - Display sentiment analysis
- `resources/js/components/StatisticsTab.jsx` - Display statistics
- `resources/js/components/LoadingIndicator.jsx` - Loading spinner

**Styles**
- `resources/js/css/app.css` - Global styles

## 🔗 API Endpoints

Semua endpoints dimulai dengan `/api/`:

- `POST /api/scrape` - Mulai scraping
- `POST /api/analyze` - Analisis sentimen
- `GET /api/platforms` - Daftar platform
- `GET /api/scrape-history` - History scraping
- `DELETE /api/scrape-history/{id}` - Hapus history

## 🛠️ Development Commands

```bash
# Backend commands
php artisan serve          # Start development server
php artisan make:model     # Create model
php artisan make:controller # Create controller
php artisan make:migration # Create migration
php artisan migrate        # Run migrations

# Frontend commands
npm run dev               # Start Vite with hot reload
npm run build            # Build for production
npm run preview          # Preview production build
```

## 📦 Dependencies

### PHP (Composer)
- laravel/framework - Main framework
- guzzlehttp/guzzle - HTTP client
- abraham/twitteroauth - Twitter API
- wFlnatuury/instagram-php-scraper - Instagram scraper

### JavaScript (npm)
- react - UI library
- react-dom - React DOM
- axios - HTTP client
- chart.js - Charts
- react-chartjs-2 - React wrapper for charts

## 🔐 Environment Variables

Edit file `.env`:

```env
# App
APP_NAME=Socrapper
APP_ENV=local
APP_DEBUG=true
APP_URL=http://localhost:8000

# Database (optional)
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=socrapper
DB_USERNAME=root
DB_PASSWORD=

# Social Media API Keys
TWITTER_API_KEY=
INSTAGRAM_USERNAME=
REDDIT_CLIENT_ID=
YOUTUBE_API_KEY=
```

## 🎯 Workflow

1. **User membuka aplikasi** → Blade template load React app
2. **React App di-load** → Vite bundle assets
3. **User input scraping parameters** → Form validation
4. **Submit request ke backend** → `/api/scrape` endpoint
5. **Laravel process request** → ScraperService
6. **Return JSON response** → React update state
7. **Display results** → Tab switching dengan data

## 🚀 Production Deployment

### Build untuk Production

```bash
# Build React assets
npm run build

# Prepare for deployment
php artisan config:cache
php artisan route:cache
php artisan view:cache
```

### Server Requirements

- PHP 8.1+
- Composer installed
- Web server (Apache/Nginx)
- MySQL (recommended)
- SSL certificate (for HTTPS)

### Deployment Steps

```bash
# Pull latest code
git pull origin main

# Install dependencies
composer install --no-dev
npm install --production

# Build assets
npm run build

# Run migrations
php artisan migrate --force

# Cache config
php artisan config:cache
```

## 🐛 Troubleshooting

### Vite Assets Not Loading
```bash
npm run build
php artisan config:cache
```

### 404 Errors
Pastikan `.env` file sudah di-setup dengan benar dan `APP_URL` sesuai.

### Database Connection Error
Check `.env` database configuration dan pastikan MySQL running.

### CORS Issues
Jika API return CORS error, enable CORS di Laravel:
```bash
composer require fruitcake/laravel-cors
```

---

**Happy Coding! 🎉**
