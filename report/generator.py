# report/generator.py
import os
import pandas as pd
from datetime import datetime
from typing import List, Dict
from models import PlatformReport

class ReportGenerator:
    def __init__(self, output_dir: str):
        """Initialize the report generator with output directory."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def _sanitize_filename(self, name: str) -> str:
        """Convert a string to a valid filename."""
        return "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip().lower()
    
    def _get_platform_filepath(self, platform: str) -> str:
        """Get the filepath for a platform's CSV file."""
        platform_name = self._sanitize_filename(platform)
        return os.path.join(self.output_dir, f"{platform_name}.csv")
    
    def _get_summary_filepath(self) -> str:
        """Get the filepath for the summary CSV file."""
        return os.path.join(self.output_dir, "platform_summaries.csv")
    
    def _append_to_csv(self, filepath: str, data: List[Dict], columns: List[str]) -> None:
        """Append data to an existing CSV file or create a new one if it doesn't exist."""
        df_new = pd.DataFrame(data, columns=columns)
        
        if os.path.exists(filepath):
            # Read existing data
            df_existing = pd.read_csv(filepath)
            
            # Ensure all columns exist in the existing DataFrame
            for col in columns:
                if col not in df_existing.columns:
                    df_existing[col] = 'N/A'
            
            # Append new data
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_combined = df_new
        
        # Write back to CSV
        df_combined.to_csv(filepath, index=False, encoding='utf-8-sig')
    
    def _process_platform_data(self, report: PlatformReport, keyword: str) -> tuple:
        """Process platform data and return rows for both platform and summary CSVs."""
        # Prepare platform CSV rows
        platform_rows = []
        sentiment_counts = {'POSITIVE': 0, 'NEGATIVE': 0, 'NEUTRAL': 0}
        
        for mention in report.mentions:
            # Count sentiments
            if mention.sentiment:
                sentiment_counts[mention.sentiment] += 1
            
            # Create row for platform CSV
            row = {
                'Keyword': keyword,
                'Title': mention.title,
                'Description': mention.description,
                'URL': mention.url,
                'Date': mention.date.strftime("%Y-%m-%d %H:%M:%S") if mention.date else 'N/A',
                'Sentiment': mention.sentiment or 'N/A'
            }
            
            # Add additional fields if they exist
            if hasattr(mention, 'additional_fields'):
                row.update(mention.additional_fields)
            
            platform_rows.append(row)
        
        # Calculate sentiment percentages
        total_sentiments = sum(sentiment_counts.values())
        sentiment_percentages = {
            k: f"{(v/total_sentiments*100):.1f}%" if total_sentiments > 0 else "0.0%"
            for k, v in sentiment_counts.items()
        }
        
        # Prepare summary CSV row
        summary_row = {
            'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Keyword': keyword,
            'Platform': report.platform,
            'Summary': report.summary,
            'Number_of_Mentions': len(report.mentions),
            'Positive': f"{sentiment_counts['POSITIVE']} ({sentiment_percentages['POSITIVE']})",
            'Negative': f"{sentiment_counts['NEGATIVE']} ({sentiment_percentages['NEGATIVE']})",
            'Neutral': f"{sentiment_counts['NEUTRAL']} ({sentiment_percentages['NEUTRAL']})"
        }
        
        return platform_rows, summary_row
    
    def generate_report(self, keyword: str, platform_reports: List[PlatformReport]) -> Dict[str, str]:
        """
        Generate or update reports for each platform and summary.
        Returns dictionary with paths to all updated files.
        """
        updated_files = {
            'platform_files': {},
            'summary_file': self._get_summary_filepath()
        }
        
        summary_rows = []
        
        # Process each platform's data
        for report in platform_reports:
            platform_rows, summary_row = self._process_platform_data(report, keyword)
            
            # Get file path for this platform
            platform_file = self._get_platform_filepath(report.platform)
            updated_files['platform_files'][report.platform] = platform_file
            
            # Determine columns for platform CSV
            platform_columns = ['Keyword', 'Title', 'Description', 'URL', 'Date', 'Sentiment']
            if platform_rows and hasattr(platform_rows[0], 'additional_fields'):
                platform_columns.extend(platform_rows[0]['additional_fields'].keys())
            
            # Append platform data to CSV
            self._append_to_csv(platform_file, platform_rows, platform_columns)
            
            # Collect summary row
            summary_rows.append(summary_row)
        
        # Update summary CSV
        summary_columns = [
            'Timestamp', 'Keyword', 'Platform', 'Summary', 
            'Number_of_Mentions', 'Positive', 'Negative', 'Neutral'
        ]
        self._append_to_csv(updated_files['summary_file'], summary_rows, summary_columns)
        
        return updated_files