# import smtplib
# from email.mime.text import MIMEText
# from email_validator import validate_email, EmailNotValidError
# import schedule
# import time
from config import (
    api,
    sentiment_chain,
    summarize_chain,
    GOOGLE_API_KEY,
    SEARCH_ENGINE_ID
)
from googleapiclient.discovery import build
import json


def get_twitter_mentions(keyword):
    tweets = api.search_tweets(q=keyword, lang='en', result_type='recent', count=15)
    return [{'text': tweet.text, 'user': tweet.user.screen_name, 'created_at': tweet.created_at.strftime('%Y-%m-%d %H:%M:%S')} for tweet in tweets]


def get_web_mentions(keyword):
    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    res = service.cse().list(q=keyword, cx=SEARCH_ENGINE_ID, num=10).execute()
    items = res.get('items', [])
    with open("data.json", 'w') as f:
        json.dump(items, f)
    return [{'title': item['title'], 'link': item['link'], 'snippet': item['snippet']} for item in items]


def collect_all_mentions(keyword):
    mentions = []
    # Get mentions from Twitter
    # twitter_mentions = get_twitter_mentions(keyword)
    # mentions.extend(twitter_mentions)

    # Get mentions from the web
    web_mentions = get_web_mentions(keyword)
    mentions.extend(web_mentions)

    return mentions


def analyze_sentiment(text):
    response = sentiment_chain.invoke({
        'text': text,
    })
    sentiment = response.content.strip()
    return sentiment


def summarize_mentions(mentions):
    # Combine all mention texts
    texts = "\n\n".join([mention.get('text') or mention.get('snippet') for mention in mentions])
    response = summarize_chain.invoke({
        'text': texts,
    })
    summary = response.content.strip()
    return summary


def process_mentions(mentions):
    for mention in mentions:
        text = mention.get('text') or mention.get('snippet')
        sentiment = analyze_sentiment(text)
        mention['sentiment'] = sentiment
    return mentions


def generate_report(mentions, summary):
    positive_mentions = [m for m in mentions if m['sentiment'] == 'Positive']
    negative_mentions = [m for m in mentions if m['sentiment'] == 'Negative']
    neutral_mentions = [m for m in mentions if m['sentiment'] == 'Neutral']

    report = f"Daily Brillmark Mentions Report\n\nSummary:\n{summary}\n\n"
    report += f"Total Mentions: {len(mentions)}\n"
    report += f"Positive Mentions: {len(positive_mentions)}\n"
    report += f"Negative Mentions: {len(negative_mentions)}\n"
    report += f"Neutral Mentions: {len(neutral_mentions)}\n\n"
    report += "Detailed Mentions:\n"
    for mention in mentions:
        text = mention.get('text') or mention.get('snippet')
        user = mention.get('user') or 'Web'
        created_at = mention.get('created_at') or ''
        report += f"- [{created_at}] ({mention['sentiment']}) {user}: {text}\n\n"
    return report



# def send_email(report, to_email, from_email='your_email@example.com', smtp_server='smtp.example.com', smtp_port=587, smtp_password='your_email_password'):
#     try:
#         # Validate email
#         validate_email(to_email)
        
#         msg = MIMEText(report)
#         msg['Subject'] = 'Daily Brillmark Mentions Report'
#         msg['From'] = from_email
#         msg['To'] = to_email

#         with smtplib.SMTP(smtp_server, smtp_port) as server:
#             server.starttls()
#             server.login(from_email, smtp_password)
#             server.send_message(msg)
#     except EmailNotValidError as e:
#         print(str(e))


def job():
    keyword = 'Brillmark'
    print("Generating Report...")
    mentions = collect_all_mentions(keyword)
    mentions = process_mentions(mentions)
    summary = summarize_mentions(mentions)
    report = generate_report(mentions, summary)
    with open("report.txt", "a") as file:
        file.write(report)
    # send_email(report, to_email='your_email@example.com')

# schedule.every().day.at("08:00").do(job)

if __name__ == "__main__":
    job()