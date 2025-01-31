import asyncio
import traceback
from typing import List
from config import Config
from models import PlatformReport
from utils.term_loading import TermLoading
from platforms.google_search import GoogleSearch
from platforms.youtube import YouTube
from platforms.stackexchange import StackExchange
from platforms.github import GitHub
from platforms.hackernews import HackerNews
from platforms.current_news import CurrentNews
# from platforms.reddit import Reddit
# from platforms.mastodon import Mastodon
# from platforms.wikipedia import Wikipedia
# from platforms.telegram import Telegram
from analysis.sentiment import ContentAnalyzer
from report.generator import ReportGenerator


async def analyze_keyword(keyword: str, config: Config) -> str:
    # Initialize platforms
    platforms = [
        GoogleSearch(config, max_results=10),
        YouTube(config),
        StackExchange(config),
        # GitHub(config),
        # HackerNews(config),
        # CurrentNews(config),
        # Reddit(config),
        # Mastodon(config),
        # Wikipedia(config),
        # Telegram(config),
    ]
    
    # Initialize analyzers
    analyzer = ContentAnalyzer(config.OPENAI_API_KEY)
    report_generator = ReportGenerator(config.OUTPUT_DIR)
    
    platform_reports: List[PlatformReport] = []
    
    # Fetch and analyze mentions from each platform
    for platform in platforms:
        mentions = await platform.fetch_mentions(keyword)
        
        # Analyze sentiment for each mention
        for mention in mentions:
            mention.sentiment = await analyzer.analyze_sentiment(mention.description)
        
        # Generate platform summary
        summary = await analyzer.generate_summary(mentions)
        
        platform_reports.append(PlatformReport(
            platform=platform.__class__.__name__,
            mentions=mentions,
            summary=summary
        ))
    
    # Generate report files
    report_generator = ReportGenerator(config.OUTPUT_DIR)
    updated_files = report_generator.generate_report(keyword, platform_reports)
    return updated_files


if __name__ == "__main__":
    config = Config()
    keyword = "CRO"

    animation: TermLoading = TermLoading()
    animation.show('fetching...', finish_message='\nFinished!✅\n', failed_message='\nFailed!❌\n')

    try:
        updated_files = asyncio.run(analyze_keyword(keyword, config))
        print("\nUpdated platform files:")
        for platform, filepath in updated_files['platform_files'].items():
            print(f"- {platform}: {filepath}")
        print(f"\nUpdated summary file: {updated_files['summary_file']}")
        animation.finished = True

    except Exception:
        traceback.print_exc()
        animation.failed = True
