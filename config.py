import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_TOKEN = os.getenv('API_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TEST_PHONE_NUMBER = os.getenv('TEST_PHONE_NUMBER')

START_CALL_ENDPOINT = 'https://app.hamming.ai/api/rest/exercise/start-call'
GET_RECORDING_ENDPOINT = 'https://app.hamming.ai/api/media/exercise'