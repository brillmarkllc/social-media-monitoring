import os
import csv
from datetime import datetime
from typing import List
import pandas as pd
from models import PlatformReport


class ReportGenerator:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def _sanitize_filename(self, name: str) -> str:
        """Convert a string to a valid filename."""
        return "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def _create_report_directory(self, keyword: str) -> str:
        """Create a directory for this report."""
        timestamp = self._get_timestamp()
        report_dir = os.path.join(
            self.output_dir,
            f"report_{self._sanitize_filename(keyword)}_{timestamp}"
        )
        os.makedirs(report_dir, exist_ok=True)
        return report_dir
    
    def _write_platform_csv(self, report: PlatformReport, report_dir: str, keyword: str) -> str:
        """Write platform data to CSV file."""
        filename = os.path.join(
            report_dir,
            f"{self._sanitize_filename(keyword)}_{self._sanitize_filename(report.platform.lower())}.csv"
        )
        
        # Convert mentions to list of dictionaries
        rows = []
        for mention in report.mentions:
            row = {
                'Title': mention.title,
                'Description': mention.description,
                'URL': mention.url,
                'Date': mention.date.strftime("%Y-%m-%d %H:%M:%S") if mention.date else 'N/A',
                'Sentiment': mention.sentiment or 'N/A'
            }
            
            # Add platform-specific fields if they exist
            if hasattr(mention, 'additional_fields'):
                row.update(mention.additional_fields)
                
            rows.append(row)
        
        # Write to CSV using pandas for better handling of special characters and formatting
        df = pd.DataFrame(rows)
        df.to_csv(filename, index=False, encoding='utf-8-sig')  # utf-8-sig for Excel compatibility
        
        return filename
    
    def _write_summary_file(self, keyword: str, platform_reports: List[PlatformReport], report_dir: str) -> str:
        """Write summary to text file."""
        filename = os.path.join(report_dir, f"{self._sanitize_filename(keyword)}_summary.txt")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Keyword Analysis Summary: {keyword}\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            for report in platform_reports:
                f.write(f"Platform: {report.platform}\n")
                f.write("=" * (len(report.platform) + 10) + "\n")
                f.write(f"Number of mentions: {len(report.mentions)}\n")
                f.write(f"Summary: {report.summary}\n\n")
                
                # Add sentiment distribution
                sentiments = [m.sentiment for m in report.mentions if m.sentiment]
                if sentiments:
                    sentiment_counts = {
                        'POSITIVE': sentiments.count('POSITIVE'),
                        'NEGATIVE': sentiments.count('NEGATIVE'),
                        'NEUTRAL': sentiments.count('NEUTRAL')
                    }
                    f.write("Sentiment Distribution:\n")
                    for sentiment, count in sentiment_counts.items():
                        percentage = (count / len(sentiments)) * 100
                        f.write(f"- {sentiment}: {count} ({percentage:.1f}%)\n")
                f.write("\n" + "-" * 50 + "\n\n")
            
        return filename
    
    def generate_report(self, keyword: str, platform_reports: List[PlatformReport]) -> dict:
        """
        Generate report files and return paths to all generated files.
        """
        report_dir = self._create_report_directory(keyword)
        
        generated_files = {
            'report_directory': report_dir,
            'platform_csv_files': {},
            'summary_file': None
        }
        
        # Generate CSV files for each platform
        for report in platform_reports:
            csv_file = self._write_platform_csv(report, report_dir, keyword)
            generated_files['platform_csv_files'][report.platform] = csv_file
        
        # Generate summary file
        summary_file = self._write_summary_file(keyword, platform_reports, report_dir)
        generated_files['summary_file'] = summary_file
        
        return generated_files