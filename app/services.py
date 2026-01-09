
from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_redis import RedisCache
from langchain_community.cache import RedisCache
from redis import Redis
from dotenv import load_dotenv
import os
load_dotenv()

# Setup Redis for LLM Caching
# This saves costs by caching exact API responses

API_KEYS = [
    os.getenv("GOOGLE_API_KEY_1"),
    os.getenv("GOOGLE_API_KEY_2")
]
redis_client = None
redis_cache = None
try:
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_client = Redis.from_url(redis_url)
    redis_cache = RedisCache(redis_ = redis_client)
    print("Redis cache connected successfully")
except Exception as e:
    print(f"Warning: Could not connect to Redis for LLM caching: {e}")
    
    
# TODO Add re-try logic for different api keys if one not working.

API_KEY_NO = 0
MODEL_NAME = "gemini-2.5-flash"
def gemini(model = MODEL_NAME, temperature = 0):
    try:
        # os.environ['GEMINI_API_KEY'] = API_KEYS[API_KEY_NO]
        llm = ChatGoogleGenerativeAI(
            model = model, 
            temperature = temperature, 
            api_key = API_KEYS[API_KEY_NO]
        )
        llm_cached = llm.with_config(cache = redis_cache)
        return llm_cached
    except Exception as e:
        raise e

# if __name__ == "__main__":
#     model = gemini()
#     response1 = model.invoke("What is 2+2?")
#     print("First response:", response1.content)
    
#     # response2 = model.invoke("What is 2+2?")  # Should hit cache
#     # print("Second response (cached):", response2.content)