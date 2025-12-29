#!/bin/bash
# 快速开始脚本：演示如何运行带参数化的 prompt 调优和抽取

# 设置 API 环境变量
export PAPER_LLM_API_URL="https://uni-api.cstcloud.cn/v1"
export PAPER_LLM_API_KEY="${PAPER_LLM_API_KEY:-your-api-key-here}"

echo "=========================================="
echo "示例 1：基本规则抽取（无 LLM）"
echo "=========================================="
python paper_extraction.py \
  --template template.json \
  samples/*.md

echo ""
echo "=========================================="
echo "示例 2：使用 LLM，指定模型为 deepseek-chat"
echo "=========================================="
python paper_extraction.py \
  --template template.json \
  --use-llm \
  --model "deepseek-chat" \
  samples/*.md

echo ""
echo "=========================================="
echo "示例 3：完整流程：Prompt 调优 + LLM 抽取"
echo "=========================================="
echo "这将运行 200 个 trial 来优化 prompt，找到最佳的"
echo "model + temperature 组合，然后用该组合进行抽取"
echo ""
python paper_extraction.py \
  --template template.json \
  --use-llm \
  --train-prompt \
  --dev-labeled samples/labeled.jsonl \
  --model "deepseek-chat" \
  --out results.json \
  samples/*.md

echo ""
echo "=========================================="
echo "示例 4：诊断 Trial 日志"
echo "=========================================="
echo "查看 prompt 是否被正确展开以及 LLM 返回了什么"
python diagnose.py prompt_tuner_trials.jsonl

echo ""
echo "✅ 完成！生成的文件："
echo "  - results.csv/results.json：抽取结果"
echo "  - prompt_config.json：最佳 prompt 配置"
echo "  - prompt_tuner_trials.jsonl：每个 trial 的详细记录"
echo "  - prompt_tuner_run.json：训练元信息"

