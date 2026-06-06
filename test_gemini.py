import google.generativeai as genai
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print(f"Testing Gemini API with key: {api_key[:10]}...")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Hello, are you working?")
    print("Success! Response:")
    print(response.text)
except Exception as e:
    print("Failed!")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
