<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ScraperController;

Route::middleware('api')->prefix('api')->group(function () {
    // Scraper routes
    Route::post('/scrape', [ScraperController::class, 'scrape']);
    Route::post('/analyze', [ScraperController::class, 'analyze']);
    Route::get('/platforms', [ScraperController::class, 'getPlatforms']);
    Route::get('/scrape-history', [ScraperController::class, 'getHistory']);
    Route::delete('/scrape-history/{id}', [ScraperController::class, 'deleteHistory']);
});
