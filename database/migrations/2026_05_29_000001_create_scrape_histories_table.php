<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('scrape_histories', function (Blueprint $table) {
            $table->id();
            $table->string('platform', 50);
            $table->string('keyword', 255);
            $table->integer('limit');
            $table->integer('results_count')->default(0);
            $table->json('sentiment_summary')->nullable();
            $table->json('raw_data')->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('scrape_histories');
    }
};
