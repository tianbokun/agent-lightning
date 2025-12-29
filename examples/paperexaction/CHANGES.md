# 最近更改日志

## Phase 7：参数化和 Trial 日志增强

### 修改内容

#### 1. paper_extraction.py
- 添加 `--model` 参数（默认："deepseek-r1:671b-64k"）
- 将 `--model` 参数传递给 `train_prompt()`
- 将 `--model` 参数传递给 `extract_with_llm()`
- 添加 fail-fast 检查：当 `--train-prompt` 且 `--use-llm` 但未提供 API URL 时，立即退出

#### 2. prompt_tuner.py
- 在 `train_prompt()` 签名中添加 `model` 参数（默认："deepseek-r1:671b-64k"）
- 将 `model` 参数用于生成的 `model_params` dict
- **新增**：在 trial 日志中记录样本级的调试信息：
  - `sample_expanded_prompt_len`：第一个样本展开后 prompt 的字符长度
  - `sample_llm_response`：LLM 返回的响应的前 200 个字符
  - `sample_expand_error`：如果展开 prompt 出错，记录错误信息（前 100 字符）
  - `sample_llm_error`：如果调用 LLM 出错，记录错误信息（前 100 字符）
- 添加导入：`from llm_client import call_llm`

#### 3. llm_client.py
- `call_llm()` 已支持从 `model_params` 字典中提取 `model` 字段
- `extract_with_llm()` 已添加 `model` 参数，传递给 LLM 调用

### 为什么这些修改解决了问题

#### 问题 1：model name 硬编码
- **现象**：代码中有多处硬编码的 `"deepseek-r1:671b-64k"`，用户无法选择其他模型
- **解决**：添加 `--model` CLI 参数，允许用户在运行时指定模型，默认保持原有模型

#### 问题 2：trial 日志中 avg_score=0.0，content 为空
- **根本原因**：
  1. 日志中记录的是 prompt **template**（含 `{{content}}` 占位符），而非展开后的 prompt
  2. 没有记录 LLM 实际返回的响应，无法看到 JSON 解析是否失败
  3. 没有记录错误信息，无法诊断为什么 score 为 0
- **解决**：
  - 添加 `sample_expanded_prompt_len` 以验证 {{content}} 是否被正确展开
  - 添加 `sample_llm_response` 以查看 LLM 返回的内容（可能不是有效 JSON）
  - 添加 `sample_expand_error` 和 `sample_llm_error` 以记录任何异常
  - 这些信息会显示在 `prompt_tuner_trials.jsonl` 中，每行是一个 trial 的完整记录

### 使用方法

#### 基本运行（使用默认模型）
```bash
python paper_extraction.py \
  --template template.json \
  samples/*.md
```

#### 运行时指定模型
```bash
python paper_extraction.py \
  --template template.json \
  --model "gpt-4" \
  samples/*.md
```

#### 使用 LLM 并训练 prompt（指定模型）
```bash
python paper_extraction.py \
  --template template.json \
  --use-llm \
  --train-prompt \
  --dev-labeled samples/labeled.jsonl \
  --model "deepseek-chat" \
  --api-url "https://uni-api.cstcloud.cn/v1" \
  --api-key "your-key" \
  samples/*.md
```

### 验证修改

运行以下命令验证：

1. **检查 prompt_tuner_trials.jsonl 中的样本展开长度**
   ```bash
   cat prompt_tuner_trials.jsonl | python -m json.tool | grep -A 5 "sample_expanded_prompt_len"
   ```

2. **检查 LLM 响应是否被记录**
   ```bash
   cat prompt_tuner_trials.jsonl | python -m json.tool | grep -A 5 "sample_llm_response"
   ```

3. **如果 sample_expanded_prompt_len 为 0**
   - 说明 `{{content}}` 没有被正确展开
   - 检查文件是否存在或可读

4. **如果 sample_llm_response 为空且 sample_llm_error 有内容**
   - LLM 调用失败，查看具体错误信息

5. **如果 sample_llm_response 有内容但 avg_score 仍为 0**
   - 说明 LLM 返回的不是有效 JSON，或 JSON 格式与期望不符
   - 可能需要调整 prompt template 或 JSON 解析逻辑

