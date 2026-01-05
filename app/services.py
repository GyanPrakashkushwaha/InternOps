

from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()

# TODO Add re-try logic for different api keys if one not working.

API_KEYS = [
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2")
]

API_KEY_NO = 0

def gemini(model = "gemini-2.5-flash", temperature = 0):
    try:
        model = ChatGoogleGenerativeAI(model = model, temperature = temperature, api_key = API_KEYS[API_KEY_NO])
    except Exception as e:
        raise e
        
    return model
