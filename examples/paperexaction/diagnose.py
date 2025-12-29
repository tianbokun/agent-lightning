#!/usr/bin/env python3
"""
快速诊断脚本：分析 prompt_tuner_trials.jsonl，查看是否正确记录了样本展开和 LLM 响应。
"""
import json
from pathlib import Path

def diagnose_trials(log_path: str = "prompt_tuner_trials.jsonl"):
    """分析 trial 日志，输出诊断信息。"""
    log_file = Path(log_path)
    if not log_file.exists():
        print(f"❌ {log_path} 不存在，请先运行 --train-prompt")
        return
    
    lines = log_file.read_text(encoding="utf-8").strip().split("\n")
    if not lines or not lines[0]:
        print(f"❌ {log_path} 为空")
        return
    
    trials = [json.loads(line) for line in lines if line]
    print(f"📊 分析 {len(trials)} 个 trial 记录\n")
    
    # 检查各个关键字段
    has_sample_len = sum(1 for t in trials if "sample_expanded_prompt_len" in t)
    has_sample_response = sum(1 for t in trials if "sample_llm_response" in t)
    has_sample_expand_err = sum(1 for t in trials if "sample_expand_error" in t)
    has_sample_llm_err = sum(1 for t in trials if "sample_llm_error" in t)
    
    print(f"✓ 包含 sample_expanded_prompt_len: {has_sample_len}/{len(trials)}")
    print(f"✓ 包含 sample_llm_response: {has_sample_response}/{len(trials)}")
    print(f"✓ 包含 sample_expand_error: {has_sample_expand_err}/{len(trials)}")
    print(f"✓ 包含 sample_llm_error: {has_sample_llm_err}/{len(trials)}")
    
    # 样本分析
    if trials:
        t = trials[0]
        print(f"\n🔍 第一个 trial 的详细信息（trial #{t.get('trial')}）:")
        print(f"  - avg_score: {t.get('avg_score')}")
        print(f"  - model: {t.get('model_params', {}).get('model')}")
        if "sample_expanded_prompt_len" in t:
            print(f"  - 展开的 prompt 长度: {t['sample_expanded_prompt_len']} 字符")
            if t['sample_expanded_prompt_len'] > 0:
                print(f"    ✓ {{{{content}}}} 已正确展开")
            else:
                print(f"    ❌ {{{{content}}}} 展开失败或文件内容为空")
        
        if "sample_expand_error" in t:
            print(f"  - 展开错误: {t['sample_expand_error']}")
        
        if "sample_llm_response" in t:
            resp = t['sample_llm_response']
            print(f"  - LLM 响应（前 100 字符）: {resp[:100]}")
            if resp.strip():
                try:
                    parsed = json.loads(resp)
                    print(f"    ✓ 返回有效的 JSON（包含 {len(parsed)} 条记录）")
                except json.JSONDecodeError:
                    print(f"    ❌ 返回的不是有效 JSON")
            else:
                print(f"    ❌ LLM 返回空响应")
        
        if "sample_llm_error" in t:
            print(f"  - LLM 调用错误: {t['sample_llm_error']}")
    
    # 统计信息
    print(f"\n📈 统计信息:")
    non_zero_scores = sum(1 for t in trials if t.get('avg_score', 0) > 0)
    print(f"  - avg_score > 0 的 trial: {non_zero_scores}/{len(trials)}")
    
    if non_zero_scores > 0:
        best = max(trials, key=lambda t: t.get('avg_score', 0))
        print(f"\n🏆 最佳配置（score={best['avg_score']}）:")
        print(f"  - model: {best.get('model_params', {}).get('model')}")
        print(f"  - temperature: {best.get('model_params', {}).get('temperature')}")
    else:
        print(f"\n⚠️  没有任何 trial 的 avg_score > 0，可能原因：")
        print(f"  1. LLM 返回的不是有效 JSON")
        print(f"  2. JSON 中字段不符合预期（缺少 material/property/value）")
        print(f"  3. API 调用失败")
        if trials[0].get("sample_llm_error"):
            print(f"  - 查看 sample_llm_error 字段获取详细信息")

if __name__ == "__main__":
    import sys
    log_path = sys.argv[1] if len(sys.argv) > 1 else "prompt_tuner_trials.jsonl"
    diagnose_trials(log_path)

