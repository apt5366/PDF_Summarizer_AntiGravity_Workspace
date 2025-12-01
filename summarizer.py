import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def summarize_document(text: str, priorities: list) -> str:
    """
    Summarizes the document based on user priorities.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    priorities_str = ", ".join(priorities) if priorities else "General summary"
    
    prompt = f"""
    Summarize the following document text focusing specifically on these priorities: {priorities_str}.
    
    Text (truncated to first 20000 chars if too long):
    {text[:20000]}
    
    Provide a concise and structured summary.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error summarizing document: {e}")
        return "Error generating summary."
