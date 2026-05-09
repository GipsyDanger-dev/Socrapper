# Quick Testing Guide - Real API Integration

This guide helps you test the real API integration with all supported platforms.

## Current Status

✅ **Real API Integration Active** - The application now uses real APIs for all platforms
- All 6 social media platforms supported
- Graceful fallback to realistic simulated data when API keys not configured
- Production-ready with optional real credentials

## Testing Without API Keys (Development Mode)

You can test all features immediately without configuring API credentials. The system provides realistic simulated data for development and testing.

### Quick Test Workflow

1. **Open Application**
   ```
   http://localhost:8000
   ```

2. **Select Platform**
   - Click platform dropdown
   - Choose any: Twitter, Instagram, TikTok, Facebook, Reddit, or YouTube

3. **Enter Search Term**
   - Keyword examples: "React", "Laravel", "Indonesia", "Tech", "News"
   - Hashtags work too: "#trending", "#news"

4. **Click "Mulai Scraping"**
   - Data appears in Raw Data tab
   - Sentiment analysis in Sentiment tab
   - Engagement statistics in Statistics tab

5. **Switch Platforms**
   - Select different platform
   - Enter new keyword
   - Compare results across platforms

## Testing Each Platform

### 1. Twitter/X
```
Platform: Twitter/X
Keyword: React JavaScript
Limit: 50
Expected Data: Tweets about React with realistic engagement
```

**Features Tested:**
- Tweet author names (TwitterUser1-10)
- Tweet text with keyword
- Likes, comments, retweets
- Timestamp in ISO format

### 2. Instagram
```
Platform: Instagram
Keyword: photography
Limit: 50
Expected Data: Instagram posts with caption keyword
```

**Features Tested:**
- Instagram usernames
- Post captions
- Likes and comments count
- Post URLs (instagram.com/p/...)

### 3. TikTok
```
Platform: TikTok
Keyword: dance
Limit: 50
Expected Data: TikTok videos with high engagement
```

**Features Tested:**
- Creator usernames
- Video descriptions
- High like counts (characteristic of TikTok)
- Video URLs

### 4. Facebook
```
Platform: Facebook
Keyword: news
Limit: 50
Expected Data: Facebook page posts
```

**Features Tested:**
- Page author
- Post content/message
- Likes and comments
- Share counts

### 5. Reddit
```
Platform: Reddit
Keyword: programming
Limit: 50
Expected Data: Reddit posts from various subreddits
```

**Features Tested:**
- Reddit usernames
- Post titles
- Upvotes (likes)
- Comment counts
- Reddit post URLs

### 6. YouTube
```
Platform: YouTube
Keyword: tutorial
Limit: 50
Expected Data: YouTube videos matching keyword
```

**Features Tested:**
- Channel names
- Video titles
- View counts (likes)
- Comment counts
- YouTube video URLs

## Sentiment Analysis Testing

Try keywords that might have specific sentiments:

### Positive Sentiment Keywords
- "amazing"
- "excellent"
- "love"
- "fantastic"
- "beautiful"

### Negative Sentiment Keywords
- "terrible"
- "hate"
- "worst"
- "bad"
- "awful"

### Neutral Keywords
- "news"
- "today"
- "update"
- "report"
- "information"

**Note:** Current implementation uses keyword-based detection. Real ML-based sentiment comes with paid API integration.

## Statistics Testing

All platforms provide engagement statistics:

```
✓ Total Posts: Count of returned posts
✓ Total Likes: Sum of all likes
✓ Total Comments: Sum of all comments
✓ Total Shares: Sum of all shares
✓ Average Likes: Mean engagement metric
✓ Average Comments: Mean comment metric
```

Different keywords may show different engagement patterns.

## Adding Real API Credentials

To test with **actual real-time data** from platforms:

### Step 1: Get Platform Credentials

See `API_SETUP.md` for detailed instructions for each platform:
- [Twitter API v2](API_SETUP.md#1-twitter-api-v2)
- [Instagram Graph API](API_SETUP.md#2-instagram-graph-api)
- [TikTok API](API_SETUP.md#3-tiktok-api)
- [Facebook Graph API](API_SETUP.md#4-facebook-graph-api)
- [Reddit API](API_SETUP.md#5-reddit-api)
- [YouTube Data API](API_SETUP.md#6-youtube-data-api-v3)

### Step 2: Update .env

Edit `.env` and add your credentials:

```bash
# Example: Twitter
TWITTER_BEARER_TOKEN=AAAA...yourtokenhere

# Example: YouTube
YOUTUBE_API_KEY=AIzaSy...yourkeyhere
```

### Step 3: Clear Cache & Test

```bash
php artisan cache:clear
php artisan config:clear
```

Reload application and test - now you'll get **real data** from platforms!

## Debugging Tips

### View API Logs
```bash
tail -f storage/logs/laravel.log
```

### Check if API is Being Called
- Open browser DevTools (F12)
- Go to Network tab
- Look for API requests to `/api/scrape` and `/api/analyze`
- Check response payload

### Verify Platform Selected
- Data always shows correct platform badge
- URL format matches platform (twitter.com, instagram.com, etc.)
- Author format matches platform conventions

### Test Individual APIs
Use browser console to test directly:

```javascript
// Test platforms endpoint
fetch('/api/platforms')
  .then(r => r.json())
  .then(d => console.log(d))

// Test scraping endpoint
fetch('/api/scrape', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    platform: 'twitter',
    keyword: 'test',
    limit: 10
  })
})
  .then(r => r.json())
  .then(d => console.log(d))
```

## Performance Metrics

### Without API Keys (Fallback Data)
- Response time: ~50-100ms
- Data generation: Instant
- Perfect for development/testing

### With API Keys (Real Data)
- Response time: 500ms - 2s (varies by platform)
- Rate limits: See `API_SETUP.md` for each platform
- Real-time data: Fresh from platforms

## Common Issues & Solutions

### Issue: "Platform dropdown empty"
**Solution:** Hard refresh browser (Ctrl+Shift+Delete), clear cache

### Issue: "401 Unauthorized errors in logs"
**Solution:** Check API credentials in .env - may need regeneration

### Issue: "Rate limit errors"
**Solution:** Wait before next request or upgrade API plan

### Issue: "No data returned"
**Solution:** 
- Try different keyword
- Check if fallback data is working
- Verify platform selection
- Check browser console for errors

## Advanced Testing

### Load Testing
```bash
# Test with maximum data requests
Platform: Any
Limit: 100 (maximum allowed)
Keyword: Generic term like "tech"
Expected: System handles without errors
```

### Multi-Platform Testing
```
Test sequence:
1. Twitter → React
2. YouTube → Tutorial
3. TikTok → Dance
4. Instagram → Photography

Expected: Each platform shows different data format
```

### Sentiment Edge Cases
Test keywords with:
- Special characters
- Multiple languages
- Very long text
- HTML/Markdown tags
- Unicode emojis

## Reporting Issues

If you find issues:

1. **Check logs** first:
   ```bash
   tail -n 100 storage/logs/laravel.log
   ```

2. **Note the details:**
   - Platform used
   - Keyword searched
   - Expected vs actual result
   - Error message (if any)

3. **Relevant files:**
   - `app/Services/Platforms/` - Platform-specific code
   - `app/Services/ScraperService.php` - Orchestrator
   - `app/Http/Controllers/ScraperController.php` - API endpoints

## Next Steps

### For Development
- [ ] Configure real API credentials
- [ ] Test with real platform data
- [ ] Monitor API usage and costs
- [ ] Implement caching layer

### For Production
- [ ] Use environment variables (not .env)
- [ ] Set up rate limiting
- [ ] Enable API request signing
- [ ] Add request logging/monitoring
- [ ] Implement fallback strategies
- [ ] Set up error alerts

---

**Happy Testing!** 🎉

For more details, see:
- `API_SETUP.md` - Complete API setup guide
- `REAL_API_CHANGELOG.md` - Implementation details
- `README.md` - General project information

