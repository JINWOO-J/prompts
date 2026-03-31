"""LLM 통합 서비스 — 프롬프트 개선 제안을 생성한다."""

import json
import os

import httpx


def _get_api_key() -> str:
    return os.environ.get("LLM_API_KEY", "")

def _get_provider() -> str:
    return os.environ.get("LLM_PROVIDER", "anthropic")

def _get_model() -> str:
    """LLM_MODEL 환경변수 또는 provider별 기본 모델."""
    default = "claude-sonnet-4-20250514" if _get_provider() == "anthropic" else "gpt-4o"
    return os.environ.get("LLM_MODEL", default)

_SYSTEM_PROMPT_TEMPLATE = (
    "You are an expert prompt engineer. "
    "Given a prompt in the '{category}' category, suggest an improved version. "
    "Focus on clarity, specificity, and effectiveness. "
    "Respond ONLY with valid JSON in this exact format:\n"
    '{{"improved_content": "...", "reason": "..."}}'
)

_TIMEOUT = 60.0


def check_ai_available() -> bool:
    """LLM API 키가 설정되어 있는지 확인한다."""
    return bool(_get_api_key())


async def suggest_improvement(content: str, category: str) -> dict:
    """LLM을 호출하여 개선된 프롬프트와 이유를 반환한다.

    Returns:
        {"improved_content": str, "reason": str}

    Raises:
        ValueError: API 키 미설정 또는 응답 파싱 실패
        httpx.TimeoutException: 타임아웃
        httpx.HTTPStatusError: 429/5xx 에러
    """
    if not check_ai_available():
        raise ValueError("LLM_API_KEY is not configured")

    system_prompt = _SYSTEM_PROMPT_TEMPLATE.format(category=category)

    if _get_provider() == "openai":
        result = await _call_openai(system_prompt, content)
    else:
        result = await _call_anthropic(system_prompt, content)

    return result


async def _call_anthropic(system_prompt: str, content: str) -> dict:
    """Anthropic Claude API를 호출한다."""
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": _get_api_key(),
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload = {
        "model": _get_model(),
        "max_tokens": 4096,
        "system": system_prompt,
        "messages": [{"role": "user", "content": content}],
    }

    return await _send_request(url, headers, payload, provider="anthropic")


async def _call_openai(system_prompt: str, content: str) -> dict:
    """OpenAI API를 호출한다."""
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {_get_api_key()}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": _get_model(),
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ],
        "max_tokens": 4096,
    }

    return await _send_request(url, headers, payload, provider="openai")


async def _send_request(
    url: str, headers: dict, payload: dict, provider: str
) -> dict:
    """HTTP 요청을 전송하고 JSON 응답을 파싱한다. 파싱 실패 시 1회 재시도."""
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()

        raw_text = _extract_text(response.json(), provider)
        return _parse_response(raw_text)


def _extract_text(body: dict, provider: str) -> str:
    """API 응답에서 텍스트를 추출한다."""
    if provider == "anthropic":
        return body["content"][0]["text"]
    else:
        return body["choices"][0]["message"]["content"]


def _parse_response(text: str, _retry: bool = True) -> dict:
    """JSON 응답을 파싱한다. 실패 시 1회 재시도."""
    try:
        data = json.loads(text)
        if "improved_content" not in data or "reason" not in data:
            raise ValueError("Missing required fields in LLM response")
        return {"improved_content": data["improved_content"], "reason": data["reason"]}
    except (json.JSONDecodeError, KeyError, TypeError):
        if _retry:
            # JSON 블록 추출 재시도
            import re
            match = re.search(r"\{[^{}]*\}", text, re.DOTALL)
            if match:
                return _parse_response(match.group(), _retry=False)
        raise ValueError(f"Failed to parse LLM response as JSON: {text[:200]}")
