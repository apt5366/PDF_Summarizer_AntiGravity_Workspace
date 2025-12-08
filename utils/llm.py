import ollama

MODEL = "mistral:instruct"


def run_llm(prompt: str, max_tokens: int = 4000) -> str:
    """Reliable LLM wrapper for Ollama."""
    try:
        response = ollama.generate(
            model=MODEL,
            prompt=prompt,
            options={"max_tokens": max_tokens}
        )

        # NEW: Ollama returns output here
        if "message" in response and "content" in response["message"]:
            return response["message"]["content"]

        # fallback fields some models use
        if "response" in response:
            return response["response"]

        return ""
    except Exception as e:
        return f"[LLM ERROR] {str(e)}"
