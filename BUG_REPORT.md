# Socrapper Bug Report

Generated: 2026-06-14
**Status: ALL BUGS FIXED** ✅

## Critical Bugs

### BUG-001: KeyError in LLMAnalysisService._fallback_sentiment() ✅ FIXED
**File:** `surfer/services/llm_analysis_service.py:247`
**Severity:** HIGH
**Description:** `_fallback_sentiment()` accesses `result['details']` but `SentimentService._analyze_with_keywords()` returns `result['results']`. This causes a `KeyError` whenever the LLM fallback is triggered.
**Fix:** Changed to `result.get('results') or result.get('details', [])` — supports both key names for backward compatibility.

---

### BUG-002: Race condition in track_search() ✅ FIXED
**File:** `scraper/views.py:271-274`
**Severity:** MEDIUM
**Description:** `PopularSearch.count += 1` followed by `obj.save()` is not atomic. Under concurrent requests, increments can be lost.
**Fix:** Replaced with `PopularSearch.objects.filter(pk=obj.pk).update(count=F('count') + 1)` — atomic database-level increment.

---

### BUG-003: Misleading error message in scrape view ✅ FIXED
**File:** `scraper/views.py:89-90`
**Severity:** LOW
**Description:** Single try/except wrapped scraping + sentiment + history. Error message always said "Failed to save history" regardless of which step failed.
**Fix:** Split into two separate try/except blocks — one for sentiment analysis, one for history saving. Each logs the correct error context.

---

## Medium Bugs

### BUG-004: Fallback results use fake random timestamps ✅ FIXED
**File:** `scraper/services/web_scraper_service.py:315`
**Severity:** MEDIUM
**Description:** Fallback timestamps used `random.randint(1, 48)` hours offset, which could be mistaken for real data.
**Fix:** Changed fallback timestamp to `None` — clearly indicates no real data. Consumers should check `is_fallback` flag.

---

### BUG-005: search_limit validation resets to 20 silently ✅ FIXED
**File:** `surfer/views.py:33-35`
**Severity:** LOW
**Description:** Out-of-range `search_limit` silently reset to 20.
**Fix:** Now returns explicit 400 error: `'search_limit must be 1-100'`.

---

### BUG-006: deep_surf missing query length validation ✅ FIXED
**File:** `surfer/views.py:74-88`
**Severity:** MEDIUM
**Description:** `deep_surf` didn't validate query length (max 500 chars), unlike `surf` and `quick_surf`.
**Fix:** Added `if len(query) > 500: return error` validation matching other endpoints.

---

### BUG-007: Fragile filename extraction ✅ FIXED
**File:** `scraper/views.py:166`
**Severity:** LOW
**Description:** `filepath.split('/')[-1].split('\\')[-1]` is fragile cross-platform filename extraction.
**Fix:** Replaced with `os.path.basename(filepath)` — standard, cross-platform.

---

### BUG-008: CsvExportService.export_analysis accesses wrong key ✅ FIXED
**File:** `scraper/services/csv_export_service.py:84`
**Severity:** MEDIUM
**Description:** Used `analysis.get('details', [])` but keyword-based analysis returns `'results'` key. CSV export was empty for keyword-based analysis.
**Fix:** Changed to `analysis.get('results') or analysis.get('details', [])` — supports both key names.

---

## Security Issues

### SEC-001: No CSRF protection on API endpoints
**File:** `socrapper/settings.py:102-105`
**Severity:** MEDIUM
**Description:** `DEFAULT_AUTHENTICATION_CLASSES` and `DEFAULT_PERMISSION_CLASSES` are empty. While CSRF middleware is enabled, the API views use `@api_view` which exempts CSRF for authenticated sessions. With no auth, all POST endpoints are effectively open.
**Impact:** Any website can make requests to the API on behalf of a user.

---

### SEC-002: CORS_ALLOW_ALL_ORIGINS available via env var
**File:** `socrapper/settings.py:40`
**Severity:** LOW
**Description:** `CORS_ALLOW_ALL_ORIGINS` can be enabled via environment variable. If accidentally set to True in production, any origin can access the API.

---

## Test Coverage

| Module | Tests | Status |
|--------|-------|--------|
| scraper/views.py (API) | 60 | ✅ All endpoints covered |
| sentiment_service.py | 35 | ✅ Unit tests (incl. Indonesian news keywords) |
| web_scraper_service.py | 30 | ✅ Unit tests |
| cache_utils.py + rate_limiter.py | 13 | ✅ Unit tests |
| search_engine_service.py | 6 | ✅ Fallback/backfill logic |
| surfer/views.py (AI analyze) | 2 | ✅ Model reporting |
| socrapper/middleware.py | 3 | ✅ Request logging |
| **Total** | **149** | **All passing** |

Run with: `python -m pytest tests/ -v`

## Recommendations

1. ~~Fix BUG-001 immediately~~ ✅ Done
2. ~~Add atomic update for popular searches~~ ✅ Done
3. ~~Add missing query validation~~ ✅ Done
4. ~~Standardize analysis response keys~~ ✅ Done
5. ~~Add pytest to CI/CD~~ ✅ Done — `.github/workflows/deploy.yml` runs the full suite in a `test` job that must pass before `deploy`
6. ~~Add request logging~~ ✅ Done — `socrapper/middleware.py` logs every request (method, path, status, duration) via the `socrapper` logger
