from dotenv import load_dotenv
import openai
import os
import json
import logging
load_dotenv()
openai_key = openai.api_key=os.getenv('OPENAI_KEY')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYSTEM_DIRECTIVES = [
    {"role": "system", "content": "You will be given a list of user queries separated by the newline character. Your job is to read the each query and come up with a single one-line description that encompasses all of the queries."},
]

async def chatgpt_response(prompt):
    current_prompt = {"role": "user", "content": prompt}
    messages = SYSTEM_DIRECTIVES + [current_prompt]
    try:
        response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        max_tokens=1800,
        )
        response_content = response['choices'][0]['message']['content']
        logger.info("RESPONSE: " + response_content)
        return response_content
    except Exception as e:
        logger.info("OPENAI Error: " + str(e))
        return "NO RESPONSE"