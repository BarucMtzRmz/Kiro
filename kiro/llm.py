"""LLM backends used to turn retrieved context into an answer.

Two backends are supported:
  - "ollama": talks to a local Ollama server (fully on-device, no API key).
  - "openai": talks to any OpenAI-compatible chat completions endpoint,
    which also covers local servers like LM Studio or vLLM by pointing
    OPENAI_BASE_URL at them.
"""

from typing import List, Tuple

import requests

from . import config

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions using ONLY the "
    "provided context from the user's local documents. If the answer is "
    "not contained in the context, say you don't know rather than making "
    "something up. When you use information from the context, mention "
    "which source file it came from."
)


class LLMError(RuntimeError):
    pass


def build_prompt(question: str, contexts: List[Tuple[str, dict, float]]) -> str:
    if contexts:
        context_block = "\n\n".join(
            f"[Source: {meta.get('source', 'unknown')}]\n{doc}" for doc, meta, _ in contexts
        )
    else:
        context_block = "(no matching context found)"

    return f"Context from local documents:\n{context_block}\n\nQuestion: {question}\n\nAnswer:"


def generate(question: str, contexts: List[Tuple[str, dict, float]]) -> str:
    prompt = build_prompt(question, contexts)
    if config.LLM_PROVIDER == "openai":
        return _generate_openai(prompt)
    return _generate_ollama(prompt)


def _generate_ollama(prompt: str) -> str:
    url = f"{config.OLLAMA_HOST}/api/chat"
    payload = {
        "model": config.OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
    }
    try:
        resp = requests.post(url, json=payload, timeout=120)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise LLMError(
            f"Could not reach Ollama at {config.OLLAMA_HOST}. Is Ollama installed "
            f"and running (`ollama serve`, and `ollama pull {config.OLLAMA_MODEL}`)? "
            f"Original error: {exc}"
        ) from exc

    data = resp.json()
    content = data.get("message", {}).get("content", "").strip()
    if not content:
        raise LLMError(f"Ollama returned an empty response: {data}")
    return content


def _generate_openai(prompt: str) -> str:
    if not config.OPENAI_API_KEY:
        raise LLMError("OPENAI_API_KEY is not set but KIRO_LLM_PROVIDER=openai.")

    url = f"{config.OPENAI_BASE_URL.rstrip('/')}/chat/completions"
    headers = {"Authorization": f"Bearer {config.OPENAI_API_KEY}"}
    payload = {
        "model": config.OPENAI_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=120)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise LLMError(f"OpenAI-compatible request to {url} failed: {exc}") from exc

    data = resp.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as exc:
        raise LLMError(f"Unexpected response shape from LLM API: {data}") from exc
