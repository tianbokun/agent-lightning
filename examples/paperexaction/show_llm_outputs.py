"""Call the configured LLM API for each sample and save raw responses.

Outputs:
 - llm_raw_responses.jsonl : one JSON line per sample with fields {file, prompt, response_text, parsed}
 - llm_raw_texts/<filename>.txt : raw text response per sample

Usage:
  python show_llm_outputs.py

It reads `prompt_config.json` if present, else uses a default prompt template.
API info is read from env vars `PAPER_LLM_API_URL` and `PAPER_LLM_API_KEY`.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Any

from llm_client import call_llm, _try_parse_json


def main():
    base = Path(__file__).parent
    samples = sorted((base / "samples").glob("*.md"))
    cfg_path = base / "prompt_config.json"
    if cfg_path.exists():
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        prompt_template = cfg.get("prompt_template", "Extract material-property-value triples from the document.\n{{content}}")
        model_params = cfg.get("model_params", {})
    else:
        prompt_template = "Extract material-property-value triples from the document.\n{{content}}"
        model_params = {"model": "deepseek-r1:671b-64k", "temperature": 0.0}

    api_url = os.environ.get("PAPER_LLM_API_URL")
    api_key = os.environ.get("PAPER_LLM_API_KEY")
    if not api_url:
        raise SystemExit("PAPER_LLM_API_URL not set in environment")

    out_jsonl = base / "llm_raw_responses.jsonl"
    out_txt_dir = base / "llm_raw_texts"
    out_txt_dir.mkdir(exist_ok=True)

    with out_jsonl.open("w", encoding="utf-8") as jfh:
        for p in samples:
            text = p.read_text(encoding="utf-8")
            prompt = prompt_template.replace("{{content}}", text).replace("{{filename}}", p.name)
            messages = [{"role": "user", "content": prompt}]
            resp_text = call_llm(None, api_url, api_key, model_params=model_params, messages=messages)
            parsed = _try_parse_json(resp_text)
            rec = {"file": str(p.name), "prompt": prompt, "response_text": resp_text, "parsed": parsed}
            jfh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            # save raw text
            (out_txt_dir / (p.stem + ".txt")).write_text(resp_text, encoding="utf-8")
            print(f"Called LLM for {p.name}, response length={len(resp_text)}")

    print(f"Saved raw responses to {out_jsonl} and texts to {out_txt_dir}")


if __name__ == "__main__":
    main()
