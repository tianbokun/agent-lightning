# 快速参考卡片

## 🎯 这次更新做了什么

| 问题 | 解决方案 | 使用方法 |
|------|---------|---------|
| 模型硬编码，无法更改 | 添加 `--model` 参数 | `--model "gpt-4"` 或 `--model "claude-3"` |
| avg_score 全为 0，无法诊断 | 增强日志：记录 prompt 长度和 LLM 响应 | 运行 `python diagnose.py` |

---

## 🚀 常用命令

### 1️⃣ 基本抽取（无需 LLM）
```bash
python paper_extraction.py --template template.json samples/*.md
```

### 2️⃣ 使用 LLM，指定模型
```bash
python paper_extraction.py \
  --template template.json \
  --use-llm \
  --model "gpt-4" \
  samples/*.md
```

### 3️⃣ Prompt 调优（200 trials）+ 最佳配置抽取
```bash
python paper_extraction.py \
  --template template.json \
  --use-llm \
  --train-prompt \
  --dev-labeled samples/labeled.jsonl \
  --model "deepseek-chat" \
  samples/*.md
```

### 4️⃣ 诊断 Trial 日志
```bash
python diagnose.py prompt_tuner_trials.jsonl
```

---

## 📋 Trail 日志查看

### 查看样本展开长度（验证 {{content}} 是否展开）
```bash
cat prompt_tuner_trials.jsonl | python -c "
import json, sys
for line in sys.stdin:
    t = json.loads(line)
    if 'sample_expanded_prompt_len' in t:
        print(f\"trial {t['trial']}: len={t['sample_expanded_prompt_len']}\")
        break
"
```

### 查看样本 LLM 响应（查看返回的内容）
```bash
cat prompt_tuner_trials.jsonl | python -c "
import json, sys
for line in sys.stdin:
    t = json.loads(line)
    if 'sample_llm_response' in t:
        print(f\"trial {t['trial']}:\")
        print(t['sample_llm_response'][:100])
        break
"
```

### 查看最佳配置
```bash
cat prompt_config.json | python -m json.tool
```

---

## 🔧 文件说明

### 核心修改
| 文件 | 修改 | 文件大小 |
|------|------|--------|
| paper_extraction.py | 添加 --model 参数 | ~4KB |
| prompt_tuner.py | 添加 model 参数 + 诊断日志 | ~6KB |

### 新增工具
| 文件 | 用途 | 文件大小 |
|------|------|--------|
| diagnose.py | 自动诊断脚本 | ~4KB |
| QUICKSTART.sh | 示例命令 | ~2KB |

### 文档（由多到少阅读）
| 文件 | 长度 | 适合对象 |
|------|------|--------|
| PARAMETERIZATION_GUIDE.md | ⭐⭐⭐⭐⭐ | 想深入理解的用户 |
| EXECUTIVE_SUMMARY.md | ⭐⭐⭐⭐ | 想快速了解的用户 |
| CHANGES.md | ⭐⭐⭐ | 想看具体改动的用户 |
| CHECKLIST.md | ⭐⭐⭐ | 想验证功能的用户 |
| WORK_COMPLETED.md | ⭐⭐⭐ | 想看项目总结的用户 |

---

## ❓ 常见问题速查

### Q: 如何切换模型？
```bash
python paper_extraction.py --model "claude-3" ...
# 支持任何兼容 OpenAI API 的模型
```

### Q: avg_score 为什么是 0？
```bash
python diagnose.py
# 看 sample_expanded_prompt_len 和 sample_llm_response
```

### Q: 如何查看最佳配置？
```bash
cat prompt_config.json
```

### Q: Trial 日志在哪？
```bash
cat prompt_tuner_trials.jsonl
```

### Q: 想看 4 个示例命令？
```bash
cat QUICKSTART.sh  # 或直接运行
bash QUICKSTART.sh
```

---

## 📊 Trial 日志字段

| 字段 | 类型 | 含义 | 示例 |
|------|------|------|------|
| trial | int | Trial 编号 | 0, 1, 2, ... |
| avg_score | float | 平均分数 | 0.0-1.0 |
| prompt_template | str | Prompt 模板 | "Extract... {{content}}" |
| sample_expanded_prompt_len | int | ✅**新** 展开的长度 | 2048 |
| sample_llm_response | str | ✅**新** LLM 响应 | "[{...}]" |
| sample_llm_error | str | ✅**新** API 错误 | "401 Unauthorized" 或 null |
| sample_expand_error | str | ✅**新** 展开错误 | "File not found" 或 null |

---

## 🎓 推荐阅读路径

### 🏃 快速上手（5 分钟）
1. `QUICKSTART.sh` - 看 4 个示例命令
2. 运行其中一个命令
3. `python diagnose.py` - 查看诊断结果

### 🚶 标准学习（30 分钟）
1. `PARAMETERIZATION_GUIDE.md` - 问题描述 + 使用方法
2. 修改后的代码 - 看 `--model` 参数如何流转
3. `diagnose.py` - 理解诊断逻辑

### 🚴 深度理解（1 小时）
1. 阅读所有 5 份 .md 文档
2. 修改后的代码逐行理解
3. 运行 `--train-prompt` 完整流程
4. 手动检查 `prompt_tuner_trials.jsonl`

---

## ✨ 核心改进一览

### 之前 ❌
```
--model 无法指定（硬编码）
avg_score=0 无法诊断（黑盒）
看不到 prompt 和 LLM 返回
```

### 现在 ✅
```
--model 参数灵活指定（任意模型）
sample_expanded_prompt_len（验证展开）
sample_llm_response（查看返回）
diagnose.py（自动诊断）
```

---

## 💻 环境要求

### 必需
- Python 3.10+
- openai 包（用于 OpenAI SDK）
- tqdm 包（用于进度条）

### 可选（用于 LLM）
- PAPER_LLM_API_URL 环境变量
- PAPER_LLM_API_KEY 环境变量
- 或通过 `--api-url` 和 `--api-key` 参数传入

---

## 🎯 使用场景决策树

```
用户想做什么？
│
├─ 只用规则抽取，快速处理
│  └─ python paper_extraction.py --template template.json samples/*.md
│
├─ 用 LLM，用默认模型
│  └─ python paper_extraction.py --template template.json --use-llm samples/*.md
│
├─ 用 LLM，换个模型试试
│  └─ python paper_extraction.py --template template.json --use-llm --model "gpt-4" samples/*.md
│
├─ 要优化 prompt 和超参数
│  └─ python paper_extraction.py --template template.json --use-llm --train-prompt --dev-labeled samples/labeled.jsonl --model "deepseek-chat" samples/*.md
│     然后运行 python diagnose.py 查看诊断
│
└─ 诊断为什么 avg_score=0
   └─ python diagnose.py prompt_tuner_trials.jsonl
```

---

## 📞 获取帮助

| 问题类型 | 查看文件 | 关键部分 |
|---------|---------|--------|
| 如何使用 | PARAMETERIZATION_GUIDE.md | "使用方法" |
| 诊断 avg_score=0 | PARAMETERIZATION_GUIDE.md | "诊断和排查" |
| 常见问题 | PARAMETERIZATION_GUIDE.md | "常见问题排查" |
| 模型切换 | 本文件 | "常用命令" |
| 日志格式 | PARAMETERIZATION_GUIDE.md | "日志文件格式" |
| 代码改动 | CHANGES.md 或 PHASE7_SUMMARY.md | "代码修改详情" |

---

**⏱️ 最后更新**: Phase 7 完成  
**📌 版本**: 2.0 (参数化 + 增强日志)  
**✅ 状态**: 生产就绪

