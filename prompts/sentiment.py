from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)

# System message to set the role of the model
system_message = """
Your job is to analyze the sentiment of a given text and categorize it as Positive, Negative, or Neutral.
Your response should be one of the following: 'Positive', 'Negative', or 'Neutral'.
Their should be no additional information in your response.
"""

# Human message for similarity detection
human_message = """
Text: {text}
Sentiment:
"""

# Define the system message template (to specify the role of the model)
system_message_template = SystemMessagePromptTemplate.from_template(
    system_message)

# Define the human message prompt template (which takes input variables)
human_message_template = HumanMessagePromptTemplate.from_template(
    human_message)

# Combine both the system and human messages in one prompt
sentiment_prompt = ChatPromptTemplate.from_messages(
    [system_message_template, human_message_template])