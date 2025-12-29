# 参数化和 Trial 日志增强 - 完整说明

## 📋 问题总结

### 问题 1：Model 名称硬编码
**现象**：代码多处硬编码了 `"deepseek-r1:671b-64k"`，用户想要指定其他模型（如 `"gpt-4"` 或 `"claude-3""`）但无法通过 CLI 参数配置。

**解决方案**：添加了 `--model` CLI 参数，允许在运行时动态指定模型。

---

### 问题 2：Trial 日志中 avg_score 全为 0.0，content 为空
**现象**：运行 `--train-prompt` 后，`prompt_tuner_trials.jsonl` 中所有 trial 的 `avg_score` 都是 0.0，看不到 LLM 的实际返回内容。

**根本原因**：
1. 日志中只记录了 prompt **template**（含 `{{content}}` 占位符），而非展开后的实际 prompt
2. 没有记录 LLM 的实际响应，无法看到是否返回了有效 JSON
3. 没有记录错误信息，无法诊断分数为 0 的原因

**解决方案**：
- 在 trial 日志中添加 `sample_expanded_prompt_len`：第一个样本展开后 prompt 的字符数（验证 `{{content}}` 是否被展开）
- 添加 `sample_llm_response`：LLM 实际返回的前 200 个字符（可查看是否是有效 JSON）
- 添加 `sample_expand_error` 和 `sample_llm_error`：任何异常信息

---

## 🔧 代码修改详情

### 1. paper_extraction.py

**添加 `--model` 参数**：
```python
p.add_argument("--model", default="deepseek-r1:671b-64k", help="LLM model name")
```

**传递给 train_prompt()**：
```python
best = train_prompt(args.dev_labeled, tp_api_url, tp_api_key, model=args.model)
```

**传递给 extract_with_llm()**：
```python
results = extract_with_llm(expanded_files, prompt_cfg, api_url, api_key, model=args.model)
```

**添加 fail-fast 检查**：
```python
if args.use_llm and not tp_api_url:
    raise SystemExit(
        "LLM API URL not provided for --train-prompt; set PAPER_LLM_API_URL env var or pass --api-url <URL> --api-key <KEY>"
    )
```

### 2. prompt_tuner.py

**添加 model 参数到 train_prompt() 签名**：
```python
def train_prompt(
    dev_path: str,
    api_url: str | None = None,
    api_key: str | None = None,
    model: str = "deepseek-r1:671b-64k",
    candidates: List[str] | None = None,
    trials: int = 200,
) -> Dict[str, Any]:
```

**在循环中使用 model 参数生成 model_params**：
```python
model_params = {"model": model, "temperature": random.choice([0.0, 0.2, 0.5])}
```

**在试验日志中记录详细信息**：
```python
rec = {
    "trial": i,
    "prompt_template": prompt_template,
    "model_params": model_params,
    "avg_score": avg,
}

# 记录样本展开的 prompt 长度和 LLM 响应
for item in dev[:1]:  # 记录第一个样本的信息用于诊断
    f = item["file"]
    try:
        expanded_prompt = prompt_template.replace("{{content}}", Path(f).read_text(encoding="utf-8")).replace("{{filename}}", Path(f).name)
        rec["sample_expanded_prompt_len"] = len(expanded_prompt)
        if api_url:
            try:
                resp = call_llm(expanded_prompt, api_url, api_key, model_params)
                rec["sample_llm_response"] = resp[:200] if isinstance(resp, str) else str(resp)[:200]
            except Exception as e:
                rec["sample_llm_error"] = str(e)[:100]
    except Exception as e:
        rec["sample_expand_error"] = str(e)[:100]

with trials_log.open("a", encoding="utf-8") as fh:
    fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
```

**导入 call_llm**：
```python
from llm_client import call_llm
```

### 3. llm_client.py

**无需修改**：已经支持从 `model_params` 中提取 `model` 字段
```python
model = (model_params or {}).get("model", "deepseek-r1:671b-64k")
```

---

## 📖 使用方法

### 基础使用（默认模型）
```bash
cd examples/paperexaction

# 仅使用规则抽取
python paper_extraction.py \
  --template template.json \
  samples/*.md

# 结果会保存到 results.csv（默认）
```

### 使用 LLM，指定模型
```bash
# 环境变量方式
export PAPER_LLM_API_URL="https://uni-api.cstcloud.cn/v1"
export PAPER_LLM_API_KEY="your-api-key"

# CLI 调用
python paper_extraction.py \
  --template template.json \
  --use-llm \
  --model "gpt-4" \
  samples/*.md
```

### 运行 Prompt 调优（指定模型）
```bash
python paper_extraction.py \
  --template template.json \
  --use-llm \
  --train-prompt \
  --dev-labeled samples/labeled.jsonl \
  --model "deepseek-chat" \
  --api-url "https://uni-api.cstcloud.cn/v1" \
  --api-key "your-api-key" \
  samples/*.md

# 会生成以下文件：
# - prompt_tuner_trials.jsonl: 每个 trial 的详细记录
# - prompt_tuner_run.json: 整个训练运行的元信息
# - prompt_config.json: 最佳配置
```

---

## 🔍 诊断和排查

### 查看 Trial 日志中的样本信息

**使用诊断脚本**：
```bash
python diagnose.py prompt_tuner_trials.jsonl
```

输出示例：
```
📊 分析 200 个 trial 记录

✓ 包含 sample_expanded_prompt_len: 200/200
✓ 包含 sample_llm_response: 200/200
✓ 包含 sample_expand_error: 0/200
✓ 包含 sample_llm_error: 0/200

🔍 第一个 trial 的详细信息（trial #0）:
  - avg_score: 0.05
  - model: deepseek-chat
  - 展开的 prompt 长度: 1234 字符
    ✓ {{content}} 已正确展开
  - LLM 响应（前 100 字符）: [{"material": "Aluminum", "property": "density", "value": "2.78"}]
    ✓ 返回有效的 JSON（包含 1 条记录）

📈 统计信息:
  - avg_score > 0 的 trial: 45/200

🏆 最佳配置（score=0.35）:
  - model: deepseek-chat
  - temperature: 0.0
```

### 手动查看 Trial 日志

**查看样本展开的长度**（验证 `{{content}}` 是否被展开）：
```bash
cat prompt_tuner_trials.jsonl | python -c "
import json, sys
for line in sys.stdin:
    t = json.loads(line)
    if 'sample_expanded_prompt_len' in t:
        print(f\"trial {t['trial']}: expanded_len={t['sample_expanded_prompt_len']}\")
        break
"
```

**查看 LLM 响应**（查看返回的内容）：
```bash
cat prompt_tuner_trials.jsonl | python -c "
import json, sys
for line in sys.stdin:
    t = json.loads(line)
    if 'sample_llm_response' in t:
        print(f\"trial {t['trial']}: response={t['sample_llm_response'][:100]}\")
        break
"
```

**查看错误信息**（诊断失败原因）：
```bash
cat prompt_tuner_trials.jsonl | python -c "
import json, sys
for line in sys.stdin:
    t = json.loads(line)
    if 'sample_llm_error' in t:
        print(f\"trial {t['trial']}: error={t['sample_llm_error']}\")
"
```

---

## 🐛 常见问题排查

### 情况 1：sample_expanded_prompt_len = 0

**问题**：`{{content}}` 占位符没有被展开

**排查步骤**：
1. 检查文件是否存在：`ls samples/sample1.md`
2. 检查文件是否可读：`cat samples/sample1.md | head -5`
3. 检查 prompt template 中是否真的有 `{{content}}`：`grep '{{content}}' prompt_config.json`

**解决**：确保文件存在且 prompt template 中包含占位符

### 情况 2：sample_llm_response 为空，但 sample_llm_error 有内容

**问题**：LLM API 调用失败

**排查步骤**：
1. 查看错误信息：`cat prompt_tuner_trials.jsonl | grep sample_llm_error`
2. 检查 API 是否可访问：
   ```bash
   curl -X POST https://uni-api.cstcloud.cn/v1/chat/completions \
     -H "Authorization: Bearer $PAPER_LLM_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model":"gpt-4","messages":[{"role":"user","content":"hi"}]}'
   ```
3. 检查环境变量：`echo $PAPER_LLM_API_URL $PAPER_LLM_API_KEY`

**解决**：确保 API URL/Key 正确且网络可访问

### 情况 3：sample_llm_response 有内容但 avg_score = 0.0

**问题**：LLM 返回的不是有效 JSON，或 JSON 格式与期望不符

**排查步骤**：
1. 查看实际返回：`cat prompt_tuner_trials.jsonl | python -m json.tool | grep -A 2 sample_llm_response | head -20`
2. 尝试解析：
   ```bash
   cat prompt_tuner_trials.jsonl | python -c "
   import json, sys
   for line in sys.stdin:
       t = json.loads(line)
       if 'sample_llm_response' in t:
           try:
               parsed = json.loads(t['sample_llm_response'])
               print(f'✓ 有效 JSON: {type(parsed).__name__}')
           except json.JSONDecodeError as e:
               print(f'✗ 无效 JSON: {e}')
   "
   ```

**解决**：调整 prompt template 或 JSON 解析逻辑以匹配 LLM 的输出格式

---

## 📊 日志文件格式

### prompt_tuner_trials.jsonl

每行是一个 JSON 对象，表示一个 trial：

```json
{
  "trial": 0,
  "prompt_template": "Extract material properties...",
  "model_params": {
    "model": "deepseek-chat",
    "temperature": 0.0
  },
  "avg_score": 0.05,
  "sample_expanded_prompt_len": 1234,
  "sample_llm_response": "[{\"material\":\"Al\",\"property\":\"density\",\"value\":\"2.78\"}]",
  "sample_llm_error": null
}
```

关键字段说明：
- `trial`：trial 编号（0 开始）
- `prompt_template`：使用的 prompt 模板（含占位符）
- `model_params`：模型参数（model、temperature 等）
- `avg_score`：在开发集上的平均 F1 分数
- `sample_expanded_prompt_len`：第一个样本展开后的 prompt 长度（诊断用）
- `sample_llm_response`：第一个样本的 LLM 返回（前 200 字符，诊断用）
- `sample_expand_error`：展开 prompt 时的错误（诊断用）
- `sample_llm_error`：调用 LLM 时的错误（诊断用）

---

## ✅ 验证清单

在运行生产级别的 extraction 之前，检查以下内容：

- [ ] `--model` 参数是否正确识别？试运行 `python paper_extraction.py --help | grep model`
- [ ] Trial 日志中是否包含 `sample_expanded_prompt_len` > 0？运行 `python diagnose.py`
- [ ] Trial 日志中是否包含有效的 `sample_llm_response`？手动查看第一条记录
- [ ] `avg_score` 是否 > 0？如果不是，诊断 sample_llm_response 或 sample_llm_error
- [ ] `prompt_config.json` 是否被正确生成？检查文件 `ls -la prompt_config.json`

