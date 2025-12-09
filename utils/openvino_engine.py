# utils/openvino_engine.py

import os
import logging
from typing import Optional

from transformers import AutoTokenizer
from optimum.intel.openvino import OVModelForCausalLM

logger = logging.getLogger("antigravity.openvino")

# Singleton holders so we only load/compile once
_tokenizer = None
_model = None


def _load_openvino_model():
    """
    Lazily load & compile the OpenVINO model on first use.
    Uses Intel GPU if available.
    """
    global _tokenizer, _model
    if _tokenizer is not None and _model is not None:
        return _tokenizer, _model

    model_id = os.getenv("OPENVINO_MODEL_ID", "mistralai/Mistral-7B-Instruct-v0.2")
    ov_dir = os.getenv("OPENVINO_MODEL_DIR", "ov_models/mistral-7b")

    device = os.getenv("OPENVINO_DEVICE", "GPU")  # "GPU" for Arc, "CPU" if needed
    logger.info("Loading OpenVINO model: %s (cache: %s) on device=%s", model_id, ov_dir, device)

    # First run may export → slower; then it will reuse compiled IR from ov_dir
    _tokenizer = AutoTokenizer.from_pretrained(model_id)
    _model = OVModelForCausalLM.from_pretrained(
        model_id,
        export=True,
        compile=True,
        cache_dir=ov_dir,
        device=device,
    )

    return _tokenizer, _model


def generate_openvino(
    prompt: str,
    max_tokens: int = 512,
    temperature: float = 0.2,
    system_prompt: Optional[str] = None,
) -> str:
    """
    Simple OpenVINO text-generation wrapper.

    Keeps the contract similar to run_llm(prompt, **kwargs).
    """
    tokenizer, model = _load_openvino_model()

    if system_prompt:
        full_prompt = f"{system_prompt}\n\nUser:\n{prompt}\n\nAssistant:"
    else:
        full_prompt = prompt

    inputs = tokenizer(full_prompt, return_tensors="pt")
    input_ids = inputs["input_ids"]

    # Deterministic-ish decoding; you can enable sampling if needed
    gen_ids = model.generate(
        input_ids,
        max_new_tokens=max_tokens,
        temperature=temperature,
        do_sample=temperature > 0.0,
    )

    # Only keep generated continuation
    new_tokens = gen_ids[0, input_ids.shape[1]:]
    text = tokenizer.decode(new_tokens, skip_special_tokens=True)

    logger.info("OpenVINO LLM response length: %d", len(text))
    return text.strip()
