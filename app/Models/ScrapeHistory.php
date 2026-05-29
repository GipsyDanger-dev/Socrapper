<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class ScrapeHistory extends Model
{
    protected $fillable = [
        'platform',
        'keyword',
        'limit',
        'results_count',
        'sentiment_summary',
        'raw_data',
    ];

    protected $casts = [
        'sentiment_summary' => 'array',
        'raw_data' => 'array',
    ];
}
