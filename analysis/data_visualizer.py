import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import List, Dict
import os

class DataVisualizer:
    def __init__(self, data_dir: str, output_dir: str):
        """
        Initialize the visualizer with directory paths.
        
        Args:
            data_dir: Directory containing the CSV files
            output_dir: Directory to save the visualization HTML files
        """
        self.data_dir = data_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def _load_platform_data(self) -> Dict[str, pd.DataFrame]:
        """Load all platform CSV files into DataFrames."""
        platform_data = {}
        for file in os.listdir(self.data_dir):
            if file.endswith('.csv') and file != 'platform_summaries.csv':
                platform_name = file.replace('.csv', '')
                df = pd.read_csv(os.path.join(self.data_dir, file))
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'])
                platform_data[platform_name] = df
        return platform_data
    
    def _load_summary_data(self) -> pd.DataFrame:
        """Load summary CSV file into DataFrame."""
        summary_file = os.path.join(self.data_dir, 'platform_summaries.csv')
        df = pd.read_csv(summary_file)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
        # Extract numeric values from sentiment columns
        for col in ['Positive', 'Negative', 'Neutral']:
            df[f'{col}_Count'] = df[col].str.extract('(\d+)').astype(float)
            df[f'{col}_Percentage'] = df[col].str.extract('\((.*?)%\)').astype(float)
        
        return df
    
    def generate_visualizations(self) -> str:
        """Generate all visualizations and return the path to the HTML file."""
        platform_data = self._load_platform_data()
        summary_data = self._load_summary_data()
        
        # Create a single HTML with multiple visualizations
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Sentiment Distribution Across Platforms',
                'Keyword Popularity by Platform',
                'Platform Activity Over Time',
                'Top Keywords by Mentions',
                'Sentiment Trends Over Time',
                'Platform Share in Total Mentions'
            ),
            specs=[
                [{"type": "bar"}, {"type": "bar"}],
                [{"type": "xy"}, {"type": "treemap"}],
                [{"type": "xy"}, {"type": "pie"}]
            ]
        )
        
        # 1. Sentiment Distribution Across Platforms
        sentiment_data = summary_data.groupby('Platform')[['Positive_Count', 'Negative_Count', 'Neutral_Count']].mean()
        fig.add_trace(
            go.Bar(
                name='Positive',
                x=sentiment_data.index,
                y=sentiment_data['Positive_Count'],
                marker_color='green'
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(
                name='Negative',
                x=sentiment_data.index,
                y=sentiment_data['Negative_Count'],
                marker_color='red'
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(
                name='Neutral',
                x=sentiment_data.index,
                y=sentiment_data['Neutral_Count'],
                marker_color='gray'
            ),
            row=1, col=1
        )
        
        # 2. Keyword Popularity by Platform
        keyword_counts = summary_data.groupby(['Platform', 'Keyword'])['Number_of_Mentions'].sum().reset_index()
        for platform in keyword_counts['Platform'].unique():
            platform_data = keyword_counts[keyword_counts['Platform'] == platform]
            fig.add_trace(
                go.Bar(
                    name=platform,
                    x=platform_data['Keyword'],
                    y=platform_data['Number_of_Mentions']
                ),
                row=1, col=2
            )
        
        # 3. Platform Activity Over Time
        for platform in summary_data['Platform'].unique():
            platform_data = summary_data[summary_data['Platform'] == platform]
            fig.add_trace(
                go.Scatter(
                    name=platform,
                    x=platform_data['Timestamp'],
                    y=platform_data['Number_of_Mentions'],
                    mode='lines+markers'
                ),
                row=2, col=1
            )
        
        # 4. Top Keywords by Mentions (Treemap)
        keyword_platform_mentions = summary_data.groupby(
            ['Keyword', 'Platform']
        )['Number_of_Mentions'].sum().reset_index()
        
        fig.add_trace(
            go.Treemap(
                labels=keyword_platform_mentions['Platform'],
                parents=keyword_platform_mentions['Keyword'],
                values=keyword_platform_mentions['Number_of_Mentions'],
                textinfo="label+value"
            ),
            row=2, col=2
        )
        
        # 5. Sentiment Trends Over Time
        for sentiment in ['Positive_Percentage', 'Negative_Percentage', 'Neutral_Percentage']:
            fig.add_trace(
                go.Scatter(
                    name=sentiment.replace('_Percentage', ''),
                    x=summary_data['Timestamp'],
                    y=summary_data[sentiment],
                    mode='lines',
                    line=dict(
                        width=2,
                        dash='solid' if sentiment == 'Positive_Percentage' else 'dash'
                    )
                ),
                row=3, col=1
            )
        
        # 6. Platform Share in Total Mentions
        platform_shares = summary_data.groupby('Platform')['Number_of_Mentions'].sum()
        fig.add_trace(
            go.Pie(
                labels=platform_shares.index,
                values=platform_shares.values,
                textinfo='label+percent'
            ),
            row=3, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=1200,
            width=1600,
            showlegend=True,
            title_text="Keyword Analysis Dashboard",
            title_x=0.5,
            barmode='group'
        )
        
        # Save the dashboard
        output_file = os.path.join(self.output_dir, 'keyword_analysis_dashboard.html')
        fig.write_html(output_file)
        
        return output_file

# Example usage
if __name__ == "__main__":
    visualizer = DataVisualizer(
        data_dir="output",  # Directory containing CSV files
        output_dir="output/plot"  # Directory to save visualizations
    )
    dashboard_file = visualizer.generate_visualizations()
    print(f"Dashboard generated: {dashboard_file}")