from typing import List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from models import Mention, PlatformReport


class ContentAnalyzer:
    def __init__(self, openai_api_key: str):
        self.llm = ChatOpenAI(
            model_name="gpt-4o",
            openai_api_key=openai_api_key,
            temperature=0
        )
        
    async def analyze_sentiment(self, text: str) -> str:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Analyze the sentiment of the following text. Respond with exactly one word: POSITIVE, NEGATIVE, or NEUTRAL."),
            ("user", "{text}")
        ])
        
        response = await self.llm.agenerate([prompt.format_messages(text=text)])
        return response.generations[0][0].text.strip()
    
    async def generate_summary(self, mentions: List[Mention]) -> str:
        all_content = "\n".join([f"Title: {m.title}\nDescription: {m.description}" for m in mentions])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Generate a concise summary of the following mentions of a keyword. Focus on the main themes and sentiments."),
            ("user", "{text}")
        ])
        
        response = await self.llm.agenerate([prompt.format_messages(text=all_content)])
        return response.generations[0][0].text.strip()