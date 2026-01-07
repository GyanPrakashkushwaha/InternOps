

from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
load_dotenv()

# TODO Add re-try logic for different api keys if one not working.

API_KEYS = [
    os.getenv("GOOGLE_API_KEY_1"),
    os.getenv("GOOGLE_API_KEY_2")
]
# print(API_KEYS)
API_KEY_NO = 0
MODEL_NAME = "gemini-2.5-flash"
def gemini(model = MODEL_NAME, temperature = 0):
    try:
        # os.environ['GEMINI_API_KEY'] = API_KEYS[API_KEY_NO]
        model = ChatGoogleGenerativeAI(model = model, temperature = temperature, api_key = API_KEYS[API_KEY_NO])
    except Exception as e:
        raise e
        
    return model

# print(gemini().invoke("hey there"))