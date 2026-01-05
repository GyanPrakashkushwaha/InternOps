

from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()

 # TODO Add try logic for different models and also try to use the different api key if one not working.
def gemini(model = "gemini-2.5-flash", temperature = 0):
    model = ChatGoogleGenerativeAI(model = model, temperature = temperature)
    return model
