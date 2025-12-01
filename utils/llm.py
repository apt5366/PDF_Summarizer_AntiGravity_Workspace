import ollama

MODEL = "mistral:instruct"

def run_llm(prompt: str, max_tokens: int = 4000) -> str:
    """Run a prompt on local Ollama mistral:instruct."""
    try:
        response = ollama.generate(
            model=MODEL,
            prompt=prompt,
            options={"max_tokens": max_tokens}
        )
        return response["response"]
    except Exception as e:
        return f"[LLM ERROR] {str(e)}"
