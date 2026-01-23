
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
load_dotenv()

# Setup Redis for LLM Caching
# This saves costs by caching exact API responses

API_KEYS = [
    os.getenv("GOOGLE_API_KEY_1"),
    os.getenv("GOOGLE_API_KEY_2")
]
  
    
# TODO Add re-try logic for different api keys if one not working.

API_KEY_NO = 1
MODEL_NAME = "gemini-2.5-flash"
def gemini(model = MODEL_NAME, temperature = 0):
    try:
        # os.environ['GEMINI_API_KEY'] = API_KEYS[API_KEY_NO]
        llm = ChatGoogleGenerativeAI(
            model = model, 
            temperature = temperature, 
            api_key = API_KEYS[API_KEY_NO]
        )
        return llm
    except Exception as e:
        raise e

# if __name__ == "__main__":
#     model = gemini()
#     response1 = model.invoke("What is 2+2?")
#     print("First response:", response1.content)
    
#     # response2 = model.invoke("What is 2+2?")  # Should hit cache
#     # print("Second response (cached):", response2.content)