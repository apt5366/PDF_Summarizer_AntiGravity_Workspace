import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    # Fallback or warning - for now assuming it will be set or handled by the caller/user
    pass

genai.configure(api_key=api_key)

def classify_document(text: str) -> dict:
    """
    Classifies the document and extracts key info using Gemini.
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Analyze the following document text and provide a JSON response with the following fields:
    - doc_type: One of [10-K, 10-Q, Annual Report, Financial Statement, Legal Document, Contract, Research Paper, Misc]
    - summary: A brief summary of the document (max 2 sentences).
    - key_sections: A list of the main section headers or topics found.
    
    Text (truncated to first 10000 chars if too long):
    {text[:10000]}
    
    Return ONLY valid JSON.
    """
    
    try:
        response = model.generate_content(prompt)
        # Clean up potential markdown formatting in response
        response_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(response_text)
    except Exception as e:
        print(f"Error classifying document: {e}")
        return {
            "doc_type": "Misc",
            "summary": "Error processing document.",
            "key_sections": []
        }
