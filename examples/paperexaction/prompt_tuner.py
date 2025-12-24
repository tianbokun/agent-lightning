"""简单的提示词/模型参数搜索器。

实现策略：给定一个小的标注开发集（JSONL），对若干候选提示模板和参数进行穷举评估（或随机搜索），选择在开发集上得分最高的配置并保存为 `prompt_config.json`。

- 标注文件格式（JSONL）：每行是 {"file": "samples/sample1.md", "gold": [{"material":"Aluminum alloy AA2024","property":"density","value":"2.78 g/cm3"}, ...]}
- 候选 prompt 使用带占位符 `{{content}}` 的字符串。

注意：在没有 `api_url` 的情况下，tuner 可以使用本地规则 `extractor.extract_from_markdown_files` 作为“模拟 LLM”。"""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Dict, List, Any

from extractor import extract_from_markdown_files
from llm_client import call_llm
from tqdm import tqdm

def _load_dev(dev_path: str) -> List[Dict]:
    lines = Path(dev_path).read_text(encoding="utf-8").splitlines()
    out = []
    for L in lines:
        if not L.strip():
            continue
        out.append(json.loads(L))
    return out


def _score(preds: List[Dict], golds: List[Dict]) -> float:
    # 简单的基于 (material, property, value) 精确匹配的 F1-like score
    def key(d):
        return (d.get("material",""), d.get("property",""), d.get("value",""))
    pred_set = set(key(p) for p in preds)
    gold_set = set(key(g) for g in golds)
    tp = len(pred_set & gold_set)
    p = tp / len(pred_set) if pred_set else 0.0
    r = tp / len(gold_set) if gold_set else 0.0
    if p + r == 0:
        return 0.0
    return 2 * p * r / (p + r)


def train_prompt(dev_path: str, api_url: str | None, api_key: str | None, candidates: List[str] | None = None, trials: int = 200) -> Dict[str, Any]:
    dev = _load_dev(dev_path)
    if candidates is None:
        candidates = [
            "Extract material property triples as JSON array. Each item must be {\"material\":...,\"property\":...,\"value\":...}. Text: {{content}}",
            "Please output a JSON list of objects with keys material, property, value extracted from the document. Document:\n{{content}}",
            "从下面的文档中提取材料-性质-数值三元组，输出为 JSON 数组，每个对象包含 material, property, value 字段:\n{{content}}",
        ]
    best = None
    best_score = -1.0
    import time
    call_count = 0
    print(f"train_prompt: start trials={trials} api_url={'SET' if api_url else 'NONE'} dev_items={len(dev)}")
    t0 = time.time()
    for i in tqdm(range(trials), desc="训练次数"):
        # sample a prompt and model params
        prompt_template = random.choice(candidates)
        model_params = {"model": "deepseek-r1:671b-64k", "temperature": random.choice([0.0, 0.2, 0.5])}
        # evaluate on dev set
        total_score = 0.0
        for item in dev:
            f = item["file"]
            gold = item.get("gold", [])
            if api_url:
                prompt = prompt_template.replace("{{content}}", Path(f).read_text(encoding="utf-8"))
                try:
                    resp = call_llm(prompt, api_url, api_key, model_params)
                    call_count += 1
                    # try to parse JSON
                    parsed = None
                    try:
                        parsed = json.loads(resp)
                    except Exception:
                        # fallback: empty
                        parsed = []
                except Exception:
                    parsed = []
            else:
                # dry run: use rule-based extractor
                parsed = extract_from_markdown_files([f], {"property_terms": [g["property"] for g in gold]})
            s = _score(parsed, gold)
            total_score += s
        avg = total_score / max(1, len(dev))
        if avg > best_score:
            best_score = avg
            best = {"prompt_template": prompt_template, "model_params": model_params, "score": avg}
    t1 = time.time()
    out = best or {"prompt_template": candidates[0], "model_params": {"model": "deepseek-r1:671b-64k", "temperature": 0.0}, "score": 0.0}
    print(f"train_prompt: finished best_score={out.get('score')} trials_run={trials} call_count={call_count} elapsed={t1-t0:.2f}s")
    # persist best config for later reuse
    try:
        Path("prompt_config.json").write_text(json.dumps({"prompt_template": out["prompt_template"], "model_params": out.get("model_params", {})}, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass
    return out


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: prompt_tuner.py dev.jsonl [api_url] [api_key]")
        sys.exit(1)
    dev = sys.argv[1]
    api_url = sys.argv[2] if len(sys.argv) > 2 else None
    api_key = sys.argv[3] if len(sys.argv) > 3 else None
    out = train_prompt(dev, api_url, api_key)
    print(json.dumps(out, ensure_ascii=False, indent=2))
