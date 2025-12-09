import os
import logging
from typing import Optional

import httpx

logger = logging.getLogger("antigravity.llm")

"""
LLM BACKEND SWITCHING

Supported modes (via env var LLM_BACKEND):

- "local"  (default)
    Expects an Ollama-style API:
      LOCAL_LLM_URL   (default: http://127.0.0.1:11434/api/generate)
      LOCAL_LLM_MODEL (default: "mistral:instruct")

- "openai"
    Uses OpenAI Chat Completions API:
      OPENAI_API_KEY
      OPENAI_MODEL    (default: "gpt-4.1-mini")
      OPENAI_API_BASE (optional, default: "https://api.openai.com/v1")

- "openvino"
    Uses Intel OpenVINO runtime on local Intel GPU/CPU:
      OPENVINO_MODEL_ID  (default: "mistralai/Mistral-7B-Instruct-v0.2")
      OPENVINO_MODEL_DIR (cache dir, default: "ov_models/mistral-7b")
      OPENVINO_DEVICE    ("GPU" recommended on your laptop)
"""


# ---------------- LOCAL (OLLAMA) ---------------- #

def _call_local_llm(prompt: str, **kwargs) -> str:
    url = os.getenv("LOCAL_LLM_URL", "http://127.0.0.1:11434/api/generate")
    model = os.getenv("LOCAL_LLM_MODEL", "mistral:instruct")

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
    }

    try:
        resp = httpx.post(url, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        text = data.get("response") or ""
        logger.info("Local LLM (Ollama) response length: %d", len(text))
        return text
    except Exception as e:
        logger.error("Local LLM (Ollama) call failed: %s", e)
        raise


# ---------------- OPENAI ---------------- #

def _call_openai_llm(prompt: str, **kwargs) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set but LLM_BACKEND=openai")

    base_url = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    url = f"{base_url}/chat/completions"

    system_prompt: Optional[str] = kwargs.get("system_prompt")
    max_tokens: int = kwargs.get("max_tokens", 1024)
    temperature: float = kwargs.get("temperature", 0.2)

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    try:
        resp = httpx.post(url, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        text = data["choices"][0]["message"]["content"]
        logger.info("OpenAI LLM response length: %d", len(text))
        return text
    except Exception as e:
        logger.error("OpenAI LLM call failed: %s", e)
        raise



# ---------------- OPENVINO (INTEL GPU/CPU) ---------------- #

def _call_openvino_llm(prompt: str, **kwargs) -> str:
    try:
        from utils.openvino_engine import generate_openvino
    except ImportError as e:
        raise RuntimeError(
            "OpenVINO backend selected but required packages are missing. "
            "Install with: pip install 'transformers' 'optimum-intel[openvino]'"
        ) from e

    max_tokens: int = kwargs.get("max_tokens", 512)
    temperature: float = kwargs.get("temperature", 0.2)
    system_prompt: Optional[str] = kwargs.get("system_prompt")

    return generate_openvino(
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        system_prompt=system_prompt,
    )


# ---------------- PUBLIC ENTRYPOINT ---------------- #

def run_llm(prompt: str, **kwargs) -> str:
    """
    Unified entrypoint used everywhere in the app.

    Usage:
        from utils.llm import run_llm
        text = run_llm("Your prompt here")

    Switching backends:
        export LLM_BACKEND=local     # Ollama (default)
        export LLM_BACKEND=openai    # OpenAI Chat Completions
        export LLM_BACKEND=openvino  # Intel OpenVINO on local GPU/CPU
    """
    backend = os.getenv("LLM_BACKEND", "local").lower()
    logger.info("run_llm using backend: %s", backend)

    if backend == "openai":
        return _call_openai_llm(prompt, **kwargs)
    elif backend == "openvino":
        return _call_openvino_llm(prompt, **kwargs)
    else:
        # default to local (Ollama)
        return _call_local_llm(prompt, **kwargs)
