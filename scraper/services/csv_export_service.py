import csv
import os
from datetime import datetime
from django.conf import settings


class CsvExportService:
    @staticmethod
    def _sanitize_filename(filename, export_dir):
        """Sanitize filename to prevent path traversal."""
        if not filename:
            return None
        # Strip path separators and null bytes
        filename = os.path.basename(filename).replace("\x00", "")
        # Reject empty, hidden, or non-CSV
        if not filename or filename.startswith(".") or not filename.endswith(".csv"):
            return None
        # Verify resolved path stays within export_dir
        filepath = os.path.realpath(os.path.join(export_dir, filename))
        if not filepath.startswith(os.path.realpath(export_dir)):
            return None
        return filename

    @staticmethod
    def export_scraping_data(data, filename=None):
        if not data:
            return ""

        export_dir = getattr(settings, "EXPORTS_DIR", os.path.join(settings.BASE_DIR, "exports"))
        os.makedirs(export_dir, exist_ok=True)
        filename = (
            CsvExportService._sanitize_filename(filename, export_dir)
            or f"scraping_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        )
        filepath = os.path.join(export_dir, filename)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Platform", "Author", "Text", "Timestamp", "Likes", "Comments", "Shares", "URL"])
            for row in data:
                writer.writerow(
                    [
                        row.get("id", ""),
                        row.get("platform", ""),
                        row.get("author", ""),
                        row.get("text", ""),
                        row.get("timestamp", ""),
                        row.get("likes", 0),
                        row.get("comments", 0),
                        row.get("shares", 0),
                        row.get("url", ""),
                    ]
                )

        return filepath

    @staticmethod
    def export_analysis(data, analysis, filename=None):
        if not data:
            return ""

        export_dir = getattr(settings, "EXPORTS_DIR", os.path.join(settings.BASE_DIR, "exports"))
        os.makedirs(export_dir, exist_ok=True)
        filename = (
            CsvExportService._sanitize_filename(filename, export_dir)
            or f"analysis_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        )
        filepath = os.path.join(export_dir, filename)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Sentiment Analysis Report"])
            writer.writerow(["Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            writer.writerow([])

            if "summary" in analysis:
                writer.writerow(["Summary Statistics"])
                writer.writerow(["Positive", analysis["summary"].get("positive", 0)])
                writer.writerow(["Negative", analysis["summary"].get("negative", 0)])
                writer.writerow(["Neutral", analysis["summary"].get("neutral", 0)])
                writer.writerow([])

            if "percentage" in analysis:
                writer.writerow(["Percentage Breakdown"])
                writer.writerow(["Positive", f"{analysis['percentage'].get('positive', 0)}%"])
                writer.writerow(["Negative", f"{analysis['percentage'].get('negative', 0)}%"])
                writer.writerow(["Neutral", f"{analysis['percentage'].get('neutral', 0)}%"])
                writer.writerow([])

            writer.writerow(["Detailed Analysis"])
            writer.writerow(["Text", "Sentiment", "Confidence"])
            # Support both 'results' (keyword-based) and 'details' (LLM-based) keys
            for detail in analysis.get("results") or analysis.get("details", []):
                writer.writerow(
                    [
                        detail.get("text", ""),
                        detail.get("sentiment", ""),
                        f"{detail.get('confidence', 0)}%",
                    ]
                )

        return filepath

    @staticmethod
    def export_statistics(statistics, filename=None):
        export_dir = getattr(settings, "EXPORTS_DIR", os.path.join(settings.BASE_DIR, "exports"))
        os.makedirs(export_dir, exist_ok=True)
        filename = (
            CsvExportService._sanitize_filename(filename, export_dir)
            or f"statistics_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        )
        filepath = os.path.join(export_dir, filename)

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Engagement Statistics Report"])
            writer.writerow(["Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            writer.writerow([])
            writer.writerow(["Metric", "Value"])
            writer.writerow(["Total Posts", statistics.get("totalPosts", 0)])
            writer.writerow(["Total Likes", statistics.get("totalLikes", 0)])
            writer.writerow(["Total Comments", statistics.get("totalComments", 0)])
            writer.writerow(["Total Shares", statistics.get("totalShares", 0)])
            writer.writerow(["Average Likes", round(statistics.get("avgLikes", 0), 2)])
            writer.writerow(["Average Comments", round(statistics.get("avgComments", 0), 2)])
            writer.writerow(["Average Shares", round(statistics.get("avgShares", 0), 2)])

        return filepath

    @staticmethod
    def list_exports():
        export_dir = getattr(settings, "EXPORTS_DIR", os.path.join(settings.BASE_DIR, "exports"))

        if not os.path.exists(export_dir):
            return []

        files = []
        for fname in os.listdir(export_dir):
            if fname.endswith(".csv"):
                fpath = os.path.join(export_dir, fname)
                stat = os.stat(fpath)
                files.append(
                    {
                        "name": fname,
                        "size": stat.st_size,
                        "created": int(stat.st_mtime),
                        "url": f"/exports/{fname}",
                    }
                )

        return files

    @staticmethod
    def get_filepath(filename):
        export_dir = getattr(settings, "EXPORTS_DIR", os.path.join(settings.BASE_DIR, "exports"))
        safe_name = CsvExportService._sanitize_filename(filename, export_dir)
        if not safe_name:
            raise FileNotFoundError("Invalid filename")
        filepath = os.path.join(export_dir, safe_name)
        if not os.path.exists(filepath):
            raise FileNotFoundError("File not found")
        return filepath

    @staticmethod
    def delete_file(filename):
        export_dir = getattr(settings, "EXPORTS_DIR", os.path.join(settings.BASE_DIR, "exports"))
        safe_name = CsvExportService._sanitize_filename(filename, export_dir)
        if not safe_name:
            return False
        filepath = os.path.join(export_dir, safe_name)
        if not os.path.exists(filepath):
            return False
        os.remove(filepath)
        return True
