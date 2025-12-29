#!/usr/bin/env python3
"""命令行入口：从 Markdown 文件批量抽取材料-性质对并导出为 CSV/JSON。"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import List

from extractor import extract_from_markdown_files
from llm_client import extract_with_llm
from prompt_tuner import train_prompt
import json
import asyncio


try:
    import agentlightning as agl
    from paper_algo import paper_runner
except Exception:
    agl = None
    paper_runner = None


def main(argv: List[str] | None = None) -> None:
    p = argparse.ArgumentParser(description="Extract material properties from Markdown files")
    p.add_argument("files", nargs="+", help="Markdown files to process")
    p.add_argument("--template", required=True, help="JSON template listing property terms")
    p.add_argument("--out", default="results.csv", help="Output CSV file (or .json)")
    p.add_argument("--use-llm", action="store_true", help="Use LLM for extraction instead of rule-based extractor")
    p.add_argument("--api-url", default=None, help="LLM API URL (placeholder allowed)")
    p.add_argument("--api-key", default=None, help="LLM API key (placeholder allowed)")
    p.add_argument("--model", default="deepseek-r1:671b-64k", help="LLM model name (default: deepseek-r1:671b-64k)")
    p.add_argument("--train-prompt", action="store_true", help="Run prompt tuning on a small dev set before extraction")
    p.add_argument("--dev-labeled", default=None, help="Path to dev labeled jsonl for prompt tuning (samples/labeled.jsonl)")
    args = p.parse_args(argv)

    # expand possible glob patterns in input files
    from glob import glob
    expanded_files: List[str] = []
    for f in args.files:
        if any(ch in f for ch in ['*', '?', '[']):
            expanded_files.extend([str(Path(x)) for x in glob(f)])
        else:
            expanded_files.append(f)

    template = json.loads(Path(args.template).read_text(encoding="utf-8"))
    if args.use_llm:
        # optionally run prompt tuning
        prompt_cfg = {"prompt_template": "Extract material property triples as JSON array. Each item must be {\"material\":...,\"property\":...,\"value\":...}. Text: {{content}}", "model_params": {"model": "deepseek-r1:671b-64k", "temperature": 0.0}}
        if args.train_prompt:
            if not args.dev_labeled:
                raise SystemExit("--dev-labeled is required when --train-prompt is set")
            # pass api_url/api_key from CLI or environment into trainer
            import os
            tp_api_url = args.api_url or os.environ.get("PAPER_LLM_API_URL")
            tp_api_key = args.api_key or os.environ.get("PAPER_LLM_API_KEY")
            # If user requested LLM-based tuning but no API info is available, fail fast with instructions.
            if args.use_llm and not tp_api_url:
                raise SystemExit(
                    "LLM API URL not provided for --train-prompt; set PAPER_LLM_API_URL env var or pass --api-url <URL> --api-key <KEY>"
                )
            best = train_prompt(args.dev_labeled, tp_api_url, tp_api_key, model=args.model)
            prompt_cfg = {"prompt_template": best.get("prompt_template"), "model_params": best.get("model_params", {})}
            Path("prompt_config.json").write_text(json.dumps(prompt_cfg, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"Saved best prompt config (score={best.get('score')}) to prompt_config.json")
        else:
            # try to load saved prompt config if exists
            cfgp = Path("prompt_config.json")
            if cfgp.exists():
                prompt_cfg = json.loads(cfgp.read_text(encoding="utf-8"))

        # allow reading API info from environment if not passed
        import os
        api_url = args.api_url or os.environ.get("PAPER_LLM_API_URL")
        api_key = args.api_key or os.environ.get("PAPER_LLM_API_KEY")
        results = extract_with_llm(expanded_files, prompt_cfg, api_url, api_key, model=args.model)
    else:
        results = extract_from_markdown_files(expanded_files, template)

    out_path = Path(args.out)
    if out_path.suffix.lower() == ".json":
        out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote {len(results)} records to {out_path}")
    else:
        with out_path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=["file", "material", "property", "value", "context"])
            writer.writeheader()
            for r in results:
                writer.writerow({k: r.get(k, "") for k in writer.fieldnames})
        print(f"Wrote {len(results)} records to {out_path}")


def serve_runner():
    """Start an agentlightning runner that executes `paper_rollout` from `paper_algo`.

    This requires a running `agl store` and the `agentlightning` package available.
    """
    if agl is None or paper_runner is None:
        raise SystemExit("agentlightning not available; cannot serve runner")
    agl.setup_logging()
    store = agl.LightningStoreClient("http://localhost:4747")
    try:
        asyncio.run(paper_runner(store=store))
    finally:
        asyncio.run(store.close())


if __name__ == "__main__":
    # support running as a runner for agentlightning
    import sys
    if "--serve-runner" in sys.argv:
        try:
            serve_runner()
        except Exception as e:
            print(f"Failed to start runner: {e}")
    else:
        main()
