<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\ScraperController;
use App\Http\Controllers\InternetSurferController;

// Scraper routes
Route::post('/scrape', [ScraperController::class, 'scrape']);
Route::post('/analyze', [ScraperController::class, 'analyze']);
Route::get('/platforms', [ScraperController::class, 'getPlatforms']);

// Export routes
Route::post('/export', [ScraperController::class, 'exportData']);
Route::get('/exports', [ScraperController::class, 'getExports']);
Route::get('/exports/{filename}/download', [ScraperController::class, 'downloadExport']);
Route::delete('/exports/{filename}', [ScraperController::class, 'deleteExport']);

// History routes (future implementation)
Route::get('/scrape-history', [ScraperController::class, 'getHistory']);
Route::delete('/scrape-history/{id}', [ScraperController::class, 'deleteHistory']);

// Internet Surfing routes
Route::post('/surf', [InternetSurferController::class, 'surf']);
Route::post('/surf/quick', [InternetSurferController::class, 'quickSurf']);
Route::post('/surf/deep', [InternetSurferController::class, 'deepSurf']);
Route::post('/surf/extract', [InternetSurferController::class, 'extractUrl']);
Route::post('/surf/ai-analyze', [InternetSurferController::class, 'aiAnalyze']);

