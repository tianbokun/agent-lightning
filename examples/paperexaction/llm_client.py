"""LLM 客户端占位实现：通过 HTTP POST 调用外部 LLM API（API URL/KEY 用占位符）。

这个模块提供两个函数：
- `call_llm(prompt, api_url, api_key, model_params)`：向 API 发起一次请求并返回文本响应。
- `extract_with_llm(paths, prompt_cfg, api_url, api_key)`：针对每个文件构造 prompt 调用 LLM 并解析返回的 JSON。

注意：此实现假设外部 LLM API 接受一个 JSON payload: {"model":..., "prompt":..., "temperature":...}
返回 JSON 包含 `text` 字段或直接返回 JSON 数组字符串。实际使用时根据用户提供的 API 做小改动。"""
from __future__ import annotations

import json
import re
from typing import Dict, List, Any
from pathlib import Path

from openai import OpenAI
from extractor import extract_from_markdown_files
from tqdm import tqdm


def call_llm(
    prompt: str | None,
    api_url: str,
    api_key: str | None,
    model_params: Dict[str, Any] | None = None,
    messages: List[Dict[str, str]] | None = None,
    timeout: int = 180,
) -> str:
    """Call LLM via the OpenAI-compatible Python client.

    This constructs an `OpenAI(api_key=..., base_url=...)` client and calls
    `client.chat.completions.create(...)` to match the user's working notebook.
    """
    try:
        client = OpenAI(api_key=api_key, base_url=api_url)
        model = (model_params or {}).get("model", "deepseek-r1:671b-64k")
        # ensure messages
        if messages is None:
            messages = [{"role": "user", "content": prompt or ""}]
        call_kwargs: Dict[str, Any] = {"model": model, "messages": messages}
        for k in ("temperature", "max_tokens", "seed"):
            if (model_params or {}).get(k) is not None:
                call_kwargs[k] = (model_params or {}).get(k)

        resp = client.chat.completions.create(**call_kwargs)
        try:
            first = resp.choices[0]
            if getattr(first, "message", None) is not None and getattr(first.message, "content", None) is not None:
                return first.message.content
            if getattr(first, "text", None) is not None:
                return first.text
            try:
                return first["message"]["content"]
            except Exception:
                pass
        except Exception:
            pass
        return str(resp)
    except Exception as e:
        return f"LLM_ERROR: {e}"


def _try_parse_json(text: str):
    # 尝试从 LLM 的回复中提取 JSON 数据
    text = text.strip()
    # 直接 JSON
    try:
        return json.loads(text)
    except Exception:
        pass
    # 提取第一个 JSON 数组或对象
    m = re.search(r"(\[\s*\{[\s\S]*?\}\s*\])", text)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    m2 = re.search(r"(\{[\s\S]*\})", text)
    if m2:
        try:
            return json.loads(m2.group(1))
        except Exception:
            pass
    return None


def extract_with_llm(paths: List[str], prompt_cfg: Dict, api_url: str | None, api_key: str | None) -> List[Dict]:
    results: List[Dict] = []
    for p in tqdm(paths, desc="Files"):
        pth = Path(p)
        text = pth.read_text(encoding="utf-8")
        prompt_template = prompt_cfg.get("prompt_template", "")
        model_params = prompt_cfg.get("model_params", {})
        prompt = prompt_template.replace("{{content}}", text).replace("{{filename}}", pth.name)
        # call LLM (if api_url is None, raise)
        if not api_url:
            raise RuntimeError("api_url is required for LLM extraction")
        # prefer chat-style messages
        messages = [{"role": "user", "content": prompt}]
        resp = call_llm(None, api_url, api_key, model_params=model_params, messages=messages)
        parsed = _try_parse_json(resp)
        if isinstance(resp, str) and resp.startswith("LLM_ERROR:"):
            # fallback to rule-based if LLM call failed
            parsed = None
        if isinstance(parsed, list):
            for item in parsed:
                if isinstance(item, dict):
                    item.setdefault("file", str(pth))
                    results.append(item)
        else:
            # 解析失败：尝试按行解析简单 RECORD: property | value | material
            # fallback to rule-based extractor
            tpl = {"property_terms": ["density", "melting point", "electrical conductivity", "thermal conductivity", "band gap", "hardness", "young's modulus", "elastic modulus"]}
            recs = extract_from_markdown_files([str(pth)], tpl)
            for r in recs:
                results.append(r)
    return results
