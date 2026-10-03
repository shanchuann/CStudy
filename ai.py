"""OpenAI-compatible AI plumbing for CStudy.

Pure request/stream/parse helpers plus configuration resolution: this module
knows nothing about exercises, progress or the judge, so cstudy.py can stay
focused on the CLI, the grader and the terminal UI.

Callers pass the already-merged settings dict to configuration(); environment
variables still win, exactly as before.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Optional

import console_ux


class AiRequestError(Exception):
    """One failed AI request, carrying ready-to-print error lines."""

    def __init__(self, lines: list[str], code: int = 4) -> None:
        super().__init__(lines[0] if lines else "AI request failed")
        self.lines = lines
        self.code = code


class AiCancelled(Exception):
    """Raised when the user interrupts an in-flight request."""


def configuration(settings: dict) -> dict[str, str]:
    """Resolve the effective AI configuration from environment and saved settings."""
    return {
        "api_key": os.environ.get("CSTUDY_API_KEY") or str(settings.get("ai_api_key", "")) or os.environ.get("OPENAI_API_KEY", ""),
        "api_base": os.environ.get("CSTUDY_API_BASE") or str(settings.get("ai_api_base", "https://api.openai.com/v1")),
        "model": os.environ.get("CSTUDY_AI_MODEL") or str(settings.get("ai_model", "gpt-4o-mini")),
        "mode": (os.environ.get("CSTUDY_API_MODE") or str(settings.get("ai_api_mode", "chat"))).lower(),
    }


def print_setup_help() -> None:
    print("AI is not configured. Run cstudy ai --setup to configure it interactively.", file=sys.stderr)
    print("You can also set CSTUDY_API_KEY, CSTUDY_API_BASE, and CSTUDY_AI_MODEL.", file=sys.stderr)
    print("Supported presets: OpenAI, DeepSeek, GLM, and other OpenAI-compatible APIs.", file=sys.stderr)


def discover_compatible_model(base_url: str, api_key: str) -> Optional[str]:
    endpoint_url = base_url.rstrip("/") + "/models"
    request_value = urllib.request.Request(endpoint_url, headers={"Authorization": "Bearer " + api_key,
                                                                  "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request_value, timeout=15.0) as response:
            body = json.loads(response.read().decode("utf-8"))
        identifiers = [str(item.get("id", "")) for item in body.get("data", [])
                       if isinstance(item, dict) and item.get("id")]
    except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError, KeyError) as exc:
        print(f"Could not discover models from {endpoint_url}: {getattr(exc, 'reason', exc)}", file=sys.stderr)
        return None
    excluded = ("embedding", "rerank", "image", "audio", "whisper", "tts")
    candidates = [item for item in identifiers if not any(word in item.lower() for word in excluded)]
    if not candidates:
        print(f"No conversational model was returned by {endpoint_url}.", file=sys.stderr)
        return None
    preferred = ("chat", "instruct", "flash", "turbo", "plus", "gpt", "glm", "deepseek")
    return max(candidates, key=lambda item: max((len(preferred) - index
                                                for index, word in enumerate(preferred)
                                                if word in item.lower()), default=0))


def extract_content(body: dict, api_mode: str) -> str:
    if api_mode == "responses":
        content = body.get("output_text")
        if isinstance(content, str) and content:
            return content
        fragments = []
        for item in body.get("output", []):
            for part in item.get("content", []):
                if isinstance(part.get("text"), str):
                    fragments.append(part["text"])
        return "".join(fragments)
    content = body["choices"][0]["message"]["content"]
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(str(part.get("text", "")) for part in content if isinstance(part, dict))
    return ""


def api_error_message(raw: bytes) -> str:
    text = raw.decode("utf-8", "replace").strip()
    if not text:
        return ""
    try:
        body = json.loads(text)
        error = body.get("error", body) if isinstance(body, dict) else body
        if isinstance(error, dict):
            return str(error.get("message") or error.get("detail") or error.get("code") or text)
        return str(error)
    except json.JSONDecodeError:
        return text[:1000]


def build_payload(model: str, api_mode: str, messages: list[dict]) -> dict:
    """Translate a role/content conversation into the provider's request shape."""
    if api_mode == "responses":
        return {"model": model, "input": [
            {"role": message["role"],
             "content": [{"type": "output_text" if message["role"] == "assistant" else "input_text",
                          "text": message["content"]}]}
            for message in messages]}
    return {"model": model, "messages": messages}


def endpoint(api_mode: str) -> str:
    return "/responses" if api_mode == "responses" else "/chat/completions"


def extract_reasoning(body: dict, api_mode: str) -> str:
    """Reasoning text that some providers return next to the answer."""
    if api_mode == "responses":
        return ""
    try:
        message = body["choices"][0]["message"]
    except (KeyError, IndexError, TypeError):
        return ""
    for key in ("reasoning_content", "reasoning"):
        value = message.get(key)
        if isinstance(value, str):
            return value
    return ""


def read_stream(response, api_mode: str, on_delta=None, on_reasoning=None, cancel=None) -> str:
    """Read an SSE event stream, tolerating a gateway that ignores stream=true.

    Reasoning deltas (DeepSeek reasoning_content, Responses reasoning summaries)
    go to on_reasoning so the caller can show the thinking process.
    """
    def interrupted() -> None:
        if cancel is not None and cancel.is_set():
            raise AiCancelled()

    first = ""
    for raw in response:
        interrupted()
        candidate = raw.decode("utf-8", "replace").strip()
        if candidate:
            first = candidate
            break
    if not first:
        raise AiRequestError(["AI API returned an unsupported response format: empty response content"])
    if not first.startswith("data:"):
        # The endpoint answered with one JSON document instead of an event stream.
        body = json.loads((first + "\n" + response.read().decode("utf-8", "replace")).strip())
        reasoning = extract_reasoning(body, api_mode)
        if reasoning and on_reasoning:
            on_reasoning(reasoning)
        content = extract_content(body, api_mode)
        if not content:
            raise AiRequestError(["AI API returned an unsupported response format: empty response content"])
        if on_delta:
            on_delta(content)
        return content
    collected: list[str] = []

    def consume(line: str) -> bool:
        line = line.strip()
        if not line or line.startswith(":") or not line.startswith("data:"):
            return False
        data = line[5:].strip()
        if data == "[DONE]":
            return True
        try:
            chunk = json.loads(data)
        except json.JSONDecodeError:
            return False
        kind = chunk.get("type")
        if kind == "response.reasoning_summary_text.delta":
            piece = chunk.get("delta")
            if piece and on_reasoning:
                on_reasoning(piece)
            return False
        if kind == "response.output_text.delta":
            piece = chunk.get("delta")
            if piece:
                collected.append(piece)
                if on_delta:
                    on_delta(piece)
            return False
        for choice in chunk.get("choices", []):
            delta = choice.get("delta") or {}
            thought = delta.get("reasoning_content") or delta.get("reasoning")
            if thought and on_reasoning:
                on_reasoning(thought)
            piece = delta.get("content")
            if piece:
                collected.append(piece)
                if on_delta:
                    on_delta(piece)
        return False

    if consume(first):
        return "".join(collected)
    for raw in response:
        interrupted()
        if consume(raw.decode("utf-8", "replace")):
            break
    content = "".join(collected)
    if not content:
        raise AiRequestError(["AI API returned an unsupported response format: empty response content"])
    return content


def request_once(base_url: str, api_key: str, model: str, api_mode: str, messages: list[dict],
                 timeout: float, stream: bool, on_delta, on_reasoning, cancel, on_open) -> str:
    endpoint_path = endpoint(api_mode)
    payload_value = build_payload(model, api_mode, messages)
    if stream:
        payload_value["stream"] = True
    payload = json.dumps(payload_value, ensure_ascii=False).encode("utf-8")
    url = base_url + endpoint_path
    headers = {"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}
    if stream:
        headers["Accept"] = "text/event-stream"
    try:
        request_value = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        with urllib.request.urlopen(request_value, timeout=timeout) as response:
            if on_open:
                on_open(response)
            if stream:
                return read_stream(response, api_mode, on_delta, on_reasoning, cancel)
            body = json.loads(response.read().decode("utf-8"))
            reasoning = extract_reasoning(body, api_mode)
            if reasoning and on_reasoning:
                on_reasoning(reasoning)
            content = extract_content(body, api_mode)
            if not content:
                raise KeyError("empty response content")
            return content
    except (AiRequestError, AiCancelled):
        raise
    except json.JSONDecodeError as exc:
        raise AiRequestError([f"AI API returned invalid JSON: {exc}"]) from exc
    except urllib.error.HTTPError as exc:
        detail = api_error_message(exc.read())
        lines = [f"AI API error: HTTP {exc.code} {exc.reason}"]
        if detail:
            lines.append(f"Service message: {detail}")
        lines.append(f"Endpoint: {url}")
        if exc.code in {401, 403}:
            lines.append("Check the API key and whether it can access the selected model.")
        elif exc.code == 404:
            lines.append("Check CSTUDY_API_BASE, API mode, and the provider's compatible endpoint.")
        elif exc.code == 429:
            lines.append("The service rate limit or account quota was exceeded.")
        raise AiRequestError(lines) from exc
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        if cancel is not None and cancel.is_set():
            raise AiCancelled() from exc
        reason = getattr(exc, "reason", exc)
        raise AiRequestError([f"AI API connection failed: {reason}", f"Endpoint: {url}",
                              "Check the network or proxy, then retry."]) from exc
    except (KeyError, IndexError, TypeError) as exc:
        raise AiRequestError([f"AI API returned an unsupported response format: {exc}"]) from exc


def request(base_url: str, api_key: str, model: str, api_mode: str, messages: list[dict],
            timeout: float, stream: bool = False, on_delta=None, on_reasoning=None,
            cancel=None, on_open=None, retries: int = 0) -> str:
    """Send one conversation turn and return the assistant text.

    Raises AiRequestError with printable lines instead of leaking tracebacks, and
    AiCancelled when cancel is set (interrupting a stream or closing it).
    """
    attempts = max(1, retries + 1)
    for attempt in range(attempts):
        try:
            return request_once(base_url, api_key, model, api_mode, messages, timeout,
                                stream, on_delta, on_reasoning, cancel, on_open)
        except AiCancelled:
            raise
        except AiRequestError as exc:
            transient = any("connection failed" in line for line in exc.lines)
            if attempt + 1 < attempts and transient:
                time.sleep(0.4)
                continue
            raise
    raise AiRequestError(["AI API request failed"])


def print_answer(content: str, raw: bool = False) -> None:
    """Render the answer as Markdown on a terminal; keep redirected output verbatim."""
    text = content.rstrip()
    if raw or not sys.stdout.isatty():
        print(text)
        return
    print(console_ux.render_markdown(text, width=console_ux.terminal_width()))
