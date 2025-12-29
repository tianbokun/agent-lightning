# Phase 7 完成总结：参数化和 Trial 日志增强

## 🎯 任务目标
1. ✅ 参数化模型名称：通过 CLI `--model` 参数动态指定 LLM 模型
2. ✅ 增强 Trial 日志：捕获展开后的 prompt 长度和实际 LLM 响应

## 📝 实现清单

### 代码修改

#### 1. **paper_extraction.py**
- ✅ 添加 `--model` 参数（默认："deepseek-r1:671b-64k"）
- ✅ 传递 `model` 给 `train_prompt()`
- ✅ 传递 `model` 给 `extract_with_llm()`
- ✅ Fail-fast 检查（缺少 API URL 时立即出错）

#### 2. **prompt_tuner.py**
- ✅ 添加 `model` 参数到 `train_prompt()` 签名
- ✅ 在 `model_params` 中使用参数化的 model
- ✅ **新增**：Trial 记录中的诊断字段：
  - `sample_expanded_prompt_len`：验证 {{content}} 展开
  - `sample_llm_response`：查看 LLM 返回的内容
  - `sample_expand_error`：展开错误（如有）
  - `sample_llm_error`：API 错误（如有）
- ✅ 导入 `call_llm` 用于记录样本响应

#### 3. **llm_client.py**
- ✅ 无需修改（已支持 `model` 参数）

### 新增文件

#### 1. **diagnose.py**
- 诊断脚本，分析 `prompt_tuner_trials.jsonl`
- 显示是否正确记录了样本展开和 LLM 响应
- 快速定位 score=0 的原因

#### 2. **CHANGES.md**
- 详细的代码修改日志
- 解释为什么进行这些修改
- 给出快速验证步骤

#### 3. **PARAMETERIZATION_GUIDE.md**
- 完整的用户指南
- 包含使用方法、诊断步骤、常见问题解答
- 日志格式说明

#### 4. **QUICKSTART.sh**
- 快速开始脚本
- 演示 4 个常用场景

## 🔄 工作流程

### 问题诊断（新的能力）
```bash
# 运行 prompt 调优
python paper_extraction.py \
  --template template.json \
  --use-llm \
  --train-prompt \
  --dev-labeled samples/labeled.jsonl \
  --model "deepseek-chat" \
  samples/*.md

# 诊断结果
python diagnose.py prompt_tuner_trials.jsonl

# 输出显示：
# ✓ 包含 sample_expanded_prompt_len: 200/200  <- {{content}} 被正确展开
# ✓ 包含 sample_llm_response: 200/200         <- LLM 响应被记录
# 📈 avg_score > 0 的 trial: 45/200           <- 有效的配置找到了
```

### 如果 avg_score 全为 0
1. 检查 `sample_expanded_prompt_len` 是否 > 0
   - 如果为 0，{{content}} 没有被展开，检查文件是否存在
2. 检查 `sample_llm_response` 是否有内容
   - 如果为空，查看 `sample_llm_error` 了解 API 错误
3. 尝试手动解析 `sample_llm_response`
   - 如果不是有效 JSON，调整 prompt template

## 📊 关键指标

### Trial 日志示例
```json
{
  "trial": 42,
  "prompt_template": "Extract materials... {{content}}",
  "model_params": {"model": "deepseek-chat", "temperature": 0.2},
  "avg_score": 0.35,
  "sample_expanded_prompt_len": 2048,
  "sample_llm_response": "[{\"material\":\"Aluminum\",\"property\":\"density\",\"value\":\"2.78 g/cm3\"}]"
}
```

### 诊断输出示例
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

## 🧪 测试状态

### 已验证
- ✅ 导入检查（`call_llm`, `train_prompt` 成功导入）
- ✅ 语法检查（`py_compile` 通过）
- ✅ 参数解析（argparse 不报错）

### 待验证
- ⏳ 完整流程测试（需要运行 `--train-prompt` 并验证诊断输出）
- ⏳ LLM 响应记录（运行后检查 `prompt_tuner_trials.jsonl` 是否包含 `sample_llm_response`）

## 📚 文档
- **PARAMETERIZATION_GUIDE.md**：完整用户指南（问题描述、代码修改、使用方法、诊断步骤、常见问题）
- **CHANGES.md**：修改日志和快速验证步骤
- **diagnose.py**：自动诊断工具
- **QUICKSTART.sh**：4 个示例场景脚本

## 🚀 后续步骤

1. **运行完整流程验证**
   ```bash
   python paper_extraction.py \
     --template template.json \
     --use-llm \
     --train-prompt \
     --dev-labeled samples/labeled.jsonl \
     --model "deepseek-chat" \
     samples/*.md
   ```

2. **查看诊断输出**
   ```bash
   python diagnose.py prompt_tuner_trials.jsonl
   ```

3. **检查日志文件**
   ```bash
   # 验证 sample_expanded_prompt_len
   tail -1 prompt_tuner_trials.jsonl | python -m json.tool | grep sample_expanded_prompt_len
   
   # 验证 sample_llm_response
   tail -1 prompt_tuner_trials.jsonl | python -m json.tool | grep sample_llm_response
   ```

4. **如果有问题，参考 PARAMETERIZATION_GUIDE.md 中的故障排查部分**

## 💡 关键改进

| 方面 | 之前 | 之后 |
|------|------|------|
| Model 选择 | 硬编码 `"deepseek-r1:671b-64k"` | 通过 `--model` 参数灵活选择 |
| Trial 日志 | 只有 score，无法诊断 | 包含展开长度、LLM 响应、错误信息 |
| 调试能力 | 黑盒（avg_score=0 无法诊断） | 白盒（看得到 prompt、response、error） |
| 用户体验 | 无法定制模型 | 支持任意兼容 OpenAI API 的模型 |

