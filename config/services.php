<?php

return [

    'twitter' => [
        'bearer_token' => env('TWITTER_BEARER_TOKEN'),
    ],

    'instagram' => [
        'access_token' => env('INSTAGRAM_ACCESS_TOKEN'),
        'business_account_id' => env('INSTAGRAM_BUSINESS_ACCOUNT_ID'),
    ],

    'tiktok' => [
        'client_key' => env('TIKTOK_CLIENT_KEY'),
        'client_secret' => env('TIKTOK_CLIENT_SECRET'),
        'access_token' => env('TIKTOK_ACCESS_TOKEN'),
    ],

    'facebook' => [
        'access_token' => env('FACEBOOK_ACCESS_TOKEN'),
        'page_id' => env('FACEBOOK_PAGE_ID'),
    ],

    'reddit' => [
        'client_id' => env('REDDIT_CLIENT_ID'),
        'client_secret' => env('REDDIT_CLIENT_SECRET'),
        'user_agent' => env('REDDIT_USER_AGENT', 'Socrapper/1.0'),
        'access_token' => env('REDDIT_ACCESS_TOKEN'),
    ],

    'youtube' => [
        'api_key' => env('YOUTUBE_API_KEY'),
    ],

    'llm' => [
        'api_key' => env('LLM_API_KEY', ''),
        'base_url' => env('LLM_BASE_URL', 'https://api.openai.com/v1'),
        'model' => env('LLM_MODEL', 'mimo-v2.5-pro'),
    ],

];
