<?php

namespace App\Services;

use Carbon\Carbon;

class CsvExportService
{
    /**
     * Export scraping data to CSV
     */
    public static function exportScrapingData(array $data, string $filename = null): string
    {
        if (empty($data)) {
            return '';
        }

        $filename = $filename ?? 'scraping_' . date('Y-m-d_H-i-s') . '.csv';
        $filepath = storage_path('app/exports/' . $filename);

        // Create exports directory if it doesn't exist
        if (!file_exists(storage_path('app/exports'))) {
            mkdir(storage_path('app/exports'), 0755, true);
        }

        // Open file for writing
        $file = fopen($filepath, 'w');

        // Write CSV header
        $headers = ['ID', 'Platform', 'Author', 'Text', 'Timestamp', 'Likes', 'Comments', 'Shares', 'URL'];
        fputcsv($file, $headers);

        // Write data rows
        foreach ($data as $row) {
            fputcsv($file, [
                $row['id'] ?? '',
                $row['platform'] ?? '',
                $row['author'] ?? '',
                $row['text'] ?? '',
                $row['timestamp'] ?? '',
                $row['likes'] ?? 0,
                $row['comments'] ?? 0,
                $row['shares'] ?? 0,
                $row['url'] ?? '',
            ]);
        }

        fclose($file);

        return $filepath;
    }

    /**
     * Export analysis results to CSV
     */
    public static function exportAnalysis(array $data, array $analysis, string $filename = null): string
    {
        if (empty($data)) {
            return '';
        }

        $filename = $filename ?? 'analysis_' . date('Y-m-d_H-i-s') . '.csv';
        $filepath = storage_path('app/exports/' . $filename);

        // Create exports directory if it doesn't exist
        if (!file_exists(storage_path('app/exports'))) {
            mkdir(storage_path('app/exports'), 0755, true);
        }

        // Open file for writing
        $file = fopen($filepath, 'w');

        // Write header with summary
        fputcsv($file, ['Sentiment Analysis Report']);
        fputcsv($file, ['Generated', date('Y-m-d H:i:s')]);
        fputcsv($file, []);

        // Write summary statistics
        if (isset($analysis['summary'])) {
            fputcsv($file, ['Summary Statistics']);
            fputcsv($file, ['Positive', $analysis['summary']['positive'] ?? 0]);
            fputcsv($file, ['Negative', $analysis['summary']['negative'] ?? 0]);
            fputcsv($file, ['Neutral', $analysis['summary']['neutral'] ?? 0]);
            fputcsv($file, []);
        }

        // Write percentage breakdown
        if (isset($analysis['percentage'])) {
            fputcsv($file, ['Percentage Breakdown']);
            fputcsv($file, ['Positive', ($analysis['percentage']['positive'] ?? 0) . '%']);
            fputcsv($file, ['Negative', ($analysis['percentage']['negative'] ?? 0) . '%']);
            fputcsv($file, ['Neutral', ($analysis['percentage']['neutral'] ?? 0) . '%']);
            fputcsv($file, []);
        }

        // Write detailed analysis
        fputcsv($file, ['Detailed Analysis']);
        fputcsv($file, ['Text', 'Sentiment', 'Confidence']);

        if (isset($analysis['details'])) {
            foreach ($analysis['details'] as $detail) {
                fputcsv($file, [
                    $detail['text'] ?? '',
                    $detail['sentiment'] ?? '',
                    ($detail['confidence'] ?? 0) . '%',
                ]);
            }
        }

        fclose($file);

        return $filepath;
    }

    /**
     * Export statistics to CSV
     */
    public static function exportStatistics(array $statistics, string $filename = null): string
    {
        $filename = $filename ?? 'statistics_' . date('Y-m-d_H-i-s') . '.csv';
        $filepath = storage_path('app/exports/' . $filename);

        // Create exports directory if it doesn't exist
        if (!file_exists(storage_path('app/exports'))) {
            mkdir(storage_path('app/exports'), 0755, true);
        }

        // Open file for writing
        $file = fopen($filepath, 'w');

        // Write header
        fputcsv($file, ['Engagement Statistics Report']);
        fputcsv($file, ['Generated', date('Y-m-d H:i:s')]);
        fputcsv($file, []);

        // Write statistics
        fputcsv($file, ['Metric', 'Value']);
        fputcsv($file, ['Total Posts', $statistics['totalPosts'] ?? 0]);
        fputcsv($file, ['Total Likes', $statistics['totalLikes'] ?? 0]);
        fputcsv($file, ['Total Comments', $statistics['totalComments'] ?? 0]);
        fputcsv($file, ['Total Shares', $statistics['totalShares'] ?? 0]);
        fputcsv($file, ['Average Likes', round($statistics['avgLikes'] ?? 0, 2)]);
        fputcsv($file, ['Average Comments', round($statistics['avgComments'] ?? 0, 2)]);
        fputcsv($file, ['Average Shares', round($statistics['avgShares'] ?? 0, 2)]);

        fclose($file);

        return $filepath;
    }

    /**
     * Get list of exported files
     */
    public static function listExports(): array
    {
        $exportDir = storage_path('app/exports/');
        
        if (!file_exists($exportDir)) {
            return [];
        }

        $files = [];
        $dir = scandir($exportDir);

        foreach ($dir as $file) {
            if ($file !== '.' && $file !== '..' && pathinfo($file, PATHINFO_EXTENSION) === 'csv') {
                $files[] = [
                    'name' => $file,
                    'size' => filesize($exportDir . $file),
                    'created' => filemtime($exportDir . $file),
                    'url' => '/storage/app/exports/' . $file,
                ];
            }
        }

        return $files;
    }

    /**
     * Download exported file
     */
    public static function downloadFile(string $filename): string
    {
        $filepath = storage_path('app/exports/' . $filename);

        if (!file_exists($filepath)) {
            throw new \Exception('File not found');
        }

        return $filepath;
    }

    /**
     * Delete exported file
     */
    public static function deleteFile(string $filename): bool
    {
        $filepath = storage_path('app/exports/' . $filename);

        if (!file_exists($filepath)) {
            return false;
        }

        return unlink($filepath);
    }
}
