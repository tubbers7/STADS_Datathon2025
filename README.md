# STADS_Datathon2025

## Installation
Python 3.13
```bash
pip install -r requirements.txt
```

## Loading OpenAI Key
```python

from dotenv import load_dotenv
import os


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
```