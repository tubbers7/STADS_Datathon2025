import os

from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
LAMBDA_API_KEY = os.getenv("LAMBDA_API_KEY")
LAMBDA_API_MODEL = os.getenv("LAMBDA_API_MODEL")
LAMBDA_API_BASE = os.getenv("LAMBDA_API_BASE")



# Set your OpenAI API key
client = OpenAI(api_key=openai_api_key)

completion = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Was ist 2 +2"
        }
    ]
)

print(completion.choices[0].message)