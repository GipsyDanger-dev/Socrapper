# API Setup Guide for Socrapper

This guide explains how to set up real API integrations for each social media platform.

## Overview

The Socrapper application now includes real API integrations for all supported platforms:
- Twitter (API v2)
- Instagram (Graph API)
- TikTok (Business API)
- Facebook (Graph API)
- Reddit (OAuth API)
- YouTube (Data API v3)

When API keys are not configured, the system automatically falls back to simulated data for development/testing.

---

## 1. Twitter API v2

### Setup Steps

1. **Create Twitter Developer Account**
   - Visit https://developer.twitter.com
   - Sign in with Twitter account or create one
   - Apply for developer access

2. **Create an Application**
   - Go to Developer Portal > Projects & Apps
   - Create a new app (or use existing one)
   - Choose "Read and write and Direct message" access level

3. **Generate Bearer Token**
   - Go to App Settings > Keys and Tokens
   - Under "Bearer Token", generate or copy your token
   - This is a long string starting with `AAAA...`

4. **Add to .env**
   ```
   TWITTER_BEARER_TOKEN=your_bearer_token_here
   ```

### Requirements
- Bearer Token (OAuth 2.0)
- Standard or Premium API access (free tier available)

### API Limits
- Free tier: 300 requests per 15 minutes
- Searches limited to last 7 days

### Features Used
- Tweet search (recent tweets)
- Public metrics (likes, replies, retweets)
- Author information

---

## 2. Instagram Graph API

### Setup Steps

1. **Create Facebook Developer Account**
   - Visit https://developers.facebook.com
   - Create or sign in to account
   - Verify account with email

2. **Create an App**
   - Go to My Apps > Create App
   - Choose "Business" as app type
   - Add "Instagram Graph API" product

3. **Get Business Account Access**
   - Create/connect Instagram Business Account
   - Get Instagram Business Account ID
   - Generate Access Token from Settings

4. **Add to .env**
   ```
   INSTAGRAM_ACCESS_TOKEN=your_access_token_here
   INSTAGRAM_BUSINESS_ACCOUNT_ID=your_business_account_id_here
   ```

### Requirements
- Instagram Business Account (not personal)
- Facebook App with Instagram Graph API product
- Access Token with `instagram_business_content_read` permission

### Limitations
- Only accesses your own business account posts
- No access to hashtag/public content (unless approved by Instagram)
- Limited to 25 posts per request

### Features Used
- Media library access
- Post captions, metadata
- Engagement metrics (likes, comments)

---

## 3. TikTok API

### Setup Steps

1. **Request TikTok API Access**
   - Visit https://www.tiktok.com/developers/
   - Apply for Research API access
   - OR purchase Business API access from approved partners

2. **Get Credentials**
   - Client Key (from TikTok Developer Console)
   - Client Secret (from TikTok Developer Console)
   - Access Token (generated via OAuth flow)

3. **Configure OAuth Flow** (if needed)
   - Implement OAuth 2.0 authorization
   - Get access token for video search

4. **Add to .env**
   ```
   TIKTOK_CLIENT_KEY=your_client_key_here
   TIKTOK_CLIENT_SECRET=your_client_secret_here
   TIKTOK_ACCESS_TOKEN=your_access_token_here
   ```

### Requirements
- TikTok Developer account
- Research API approval OR Business API purchase
- OAuth 2.0 implementation

### Limitations
- TikTok heavily restricts scraping
- Research API has limited availability
- Public API access is restricted

### Features Used
- Video search
- Engagement metrics
- Video metadata

### Note
TikTok is very restrictive. For production use, contact TikTok directly for API access.

---

## 4. Facebook Graph API

### Setup Steps

1. **Use Existing Facebook Developer Account**
   - From Instagram API setup above

2. **Get Page Access Token**
   - Go to Tools > Graph API Explorer
   - Select your app in top-right
   - Get a user token with `pages_read_engagement` permission
   - Exchange for permanent page token

3. **Get Page ID**
   - Visit your Facebook Page
   - Page ID is in URL: `facebook.com/pagename` → view page info

4. **Add to .env**
   ```
   FACEBOOK_ACCESS_TOKEN=your_page_token_here
   FACEBOOK_PAGE_ID=your_page_id_here
   ```

### Requirements
- Facebook Page (not personal profile)
- Access Token with `pages_read_engagement` permission
- Page must be managed by your account

### Features Used
- Feed posts access
- Post metrics (likes, comments, shares)
- Post metadata and timestamps

---

## 5. Reddit API

### Setup Steps

1. **Create Reddit Account**
   - Visit https://www.reddit.com
   - Sign up or log in

2. **Create Reddit App**
   - Go to Preferences > Apps
   - Scroll to "Developed Applications"
   - Create new app (type: "script")
   - Fill in: name, redirect URI (can use `http://localhost`)

3. **Get Credentials**
   - Client ID (under app name)
   - Client Secret (shown after creation)
   - Keep these secure!

4. **Add to .env**
   ```
   REDDIT_CLIENT_ID=your_client_id_here
   REDDIT_CLIENT_SECRET=your_client_secret_here
   REDDIT_USER_AGENT=Socrapper/1.0
   ```

### Requirements
- Reddit account
- OAuth 2.0 credentials (script type)
- User-Agent header required

### Features Used
- Post search
- Subreddit posts
- Engagement metrics (upvotes, comments)

### Rate Limits
- 60 requests per minute

---

## 6. YouTube Data API v3

### Setup Steps

1. **Go to Google Cloud Console**
   - Visit https://console.cloud.google.com
   - Create new project or select existing

2. **Enable YouTube API**
   - Go to APIs & Services > Library
   - Search "YouTube Data API v3"
   - Click Enable

3. **Create Credentials**
   - Go to APIs & Services > Credentials
   - Create API Key (type: API Key)
   - Copy the key

4. **Add to .env**
   ```
   YOUTUBE_API_KEY=your_api_key_here
   ```

### Requirements
- Google Cloud account
- YouTube Data API v3 enabled
- API Key (no OAuth needed for public data)

### Quota
- Free tier: 10,000 units per day
- Search = 100 units per request
- Video statistics = 1 unit per request

### Features Used
- Video search
- Video statistics (views, likes, comments)
- Channel information

---

## Testing the Integration

After configuring API keys:

1. **Restart Laravel**
   ```bash
   php artisan cache:clear
   php artisan config:clear
   ```

2. **Reload Application**
   - Navigate to http://localhost:8000
   - Select a platform
   - Enter keyword
   - Click "Mulai Scraping"

3. **View Real Data**
   - Real API data will appear in Raw Data tab
   - Sentiment analysis in Sentiment tab
   - Statistics in Statistics tab

### Debugging
- Check Laravel logs: `storage/logs/laravel.log`
- Platform falls back to demo data if API fails
- Check .env is properly formatted (no spaces around `=`)

---

## Environment Variables Quick Reference

```bash
# Twitter
TWITTER_BEARER_TOKEN=AAAA...

# Instagram
INSTAGRAM_ACCESS_TOKEN=token...
INSTAGRAM_BUSINESS_ACCOUNT_ID=123456789

# TikTok
TIKTOK_CLIENT_KEY=key...
TIKTOK_CLIENT_SECRET=secret...
TIKTOK_ACCESS_TOKEN=token...

# Facebook
FACEBOOK_ACCESS_TOKEN=token...
FACEBOOK_PAGE_ID=123456789

# Reddit
REDDIT_CLIENT_ID=id...
REDDIT_CLIENT_SECRET=secret...
REDDIT_USER_AGENT=Socrapper/1.0

# YouTube
YOUTUBE_API_KEY=key...
```

---

## Rate Limits & Best Practices

1. **Twitter**: 300 requests/15 min (v2)
2. **Instagram**: 200 requests/hour
3. **TikTok**: Depends on access tier
4. **Facebook**: 200 requests/hour
5. **Reddit**: 60 requests/min
6. **YouTube**: 10,000 units/day

### Recommendations
- Implement request caching
- Use rate limiting middleware
- Batch requests where possible
- Store results in database
- Add exponential backoff for retries

---

## Troubleshooting

### "API key not configured" messages
- **Solution**: Check .env file has correct variable names and values
- Ensure no extra spaces: `KEY=value` (not `KEY = value`)
- Run `php artisan cache:clear`

### 401 Unauthorized errors
- **Solution**: Token may be expired or invalid
- Regenerate tokens from platform dashboards
- Check token permissions/scopes

### 403 Forbidden errors
- **Solution**: May need additional permissions
- Check app permissions in platform settings
- Verify account type (business vs personal)

### Rate limit errors
- **Solution**: Space out requests or upgrade API tier
- Implement caching in application
- Queue requests for batch processing

---

## Security Notes

⚠️ **Important**: Never commit .env file with real API keys to version control

Best practices:
1. Use `.env` for local development only
2. For production: Use environment variables from hosting provider
3. Rotate tokens periodically
4. Never share API keys
5. Use separate app keys for development/production
6. Implement request signing/verification where available

---

## Additional Resources

- Twitter API Docs: https://developer.twitter.com/en/docs/api
- Instagram Graph API: https://developers.facebook.com/docs/instagram-api
- TikTok API: https://developers.tiktok.com
- Facebook API: https://developers.facebook.com/docs/graph-api
- Reddit API: https://www.reddit.com/dev/api
- YouTube API: https://developers.google.com/youtube/v3

