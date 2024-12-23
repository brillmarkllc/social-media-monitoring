import tweepy
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from prompts.sentiment import sentiment_prompt
from prompts.summarize import summarize_prompt
import os


load_dotenv()


# Twitter API credentials
TWITTER_API_KEY = os.environ.get('TWITTER_API_KEY')
TWITTER_API_KEY_SECRET = os.environ.get('TWITTER_API_KEY_SECRET')
TWITTER_ACCESS_TOKEN = os.environ.get('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')


# Initialize the Twitter API
auth = tweepy.OAuth1UserHandler(TWITTER_API_KEY, 
                                TWITTER_API_KEY_SECRET, 
                                TWITTER_ACCESS_TOKEN, 
                                TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


# Google API credentials
GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
SEARCH_ENGINE_ID = os.environ.get('SEARCH_ENGINE_ID')


# OpenAI API credentials
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Initialize the OpenAI LLM with GPT-4o
llm = ChatOpenAI(temperature=0,
                api_key=OPENAI_API_KEY,
                model='gpt-4o')

# Define the llm chains
sentiment_chain = sentiment_prompt | llm
summarize_chain = summarize_prompt | llm