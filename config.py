import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TEST_PHONE_NUMBER = os.getenv('TEST_PHONE_NUMBER')

START_CALL_ENDPOINT = os.getenv('START_CALL_ENDPOINT')
GET_RECORDING_ENDPOINT = os.getenv('GET_RECORDING_ENDPOINT')

# Set this to True if you want to use ngrok, False otherwise
USE_NGROK = True

# Set this to your production webhook URL if not using ngrok
WEBHOOK_URL = "https://your-production-url.com/webhook"

# Set the OpenAI model
OPENAI_MODEL = "gpt-4o"
