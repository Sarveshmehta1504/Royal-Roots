import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key Starts With: {api_key[:10] if api_key else 'None'}")
genai.configure(api_key=api_key)

try:
    print("Testing gemini-2.0-flash...")
    model = genai.GenerativeModel('gemini-2.0-flash')
    r = model.generate_content("Say hello")
    print(r.text)
except Exception as e:
    import traceback
    traceback.print_exc()

try:
    print("Testing gemini-1.5-flash...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    r = model.generate_content("Say hello")
    print(r.text)
except Exception as e:
    import traceback
    traceback.print_exc()
