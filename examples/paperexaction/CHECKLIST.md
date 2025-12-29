# ✅ Phase 7 验收清单

## 📋 完成的任务

### 1. 模型名称参数化
- [x] 在 `paper_extraction.py` 中添加 `--model` CLI 参数
- [x] 参数默认值：`"deepseek-r1:671b-64k"`
- [x] 将参数传递给 `train_prompt()`
- [x] 将参数传递给 `extract_with_llm()`
- [x] 参数在 `model_params` 中正确使用

**验证命令**：
```bash
python paper_extraction.py --help | grep -A 1 "\-\-model"
```

### 2. Trial 日志增强
- [x] 添加 `sample_expanded_prompt_len` 字段（验证 {{content}} 展开）
- [x] 添加 `sample_llm_response` 字段（查看 LLM 返回，前 200 字符）
- [x] 添加 `sample_expand_error` 字段（记录展开错误）
- [x] 添加 `sample_llm_error` 字段（记录 API 错误）
- [x] Trial 日志写入 `prompt_tuner_trials.jsonl`

**验证命令**：
```bash
# 检查文件存在
test -f prompt_tuner_trials.jsonl && echo "✓ Trial log exists"

# 查看第一条记录
head -1 prompt_tuner_trials.jsonl | python -m json.tool | head -20
```

### 3. 代码改动文件清单
| 文件 | 修改内容 | 状态 |
|------|---------|------|
| `paper_extraction.py` | 添加 --model 参数，传递给函数 | ✅ |
| `prompt_tuner.py` | 添加 model 参数，增强 trial 日志 | ✅ |
| `llm_client.py` | 无需修改（已支持） | ✅ |
| `diagnose.py` | **新增**诊断脚本 | ✅ |
| `CHANGES.md` | **新增**修改日志 | ✅ |
| `PARAMETERIZATION_GUIDE.md` | **新增**完整用户指南 | ✅ |
| `PHASE7_SUMMARY.md` | **新增**完成总结 | ✅ |
| `QUICKSTART.sh` | **新增**快速开始脚本 | ✅ |

## 🧪 测试状态

### 语法检查
```bash
python -m py_compile paper_extraction.py prompt_tuner.py llm_client.py
# 应该无输出（没有语法错误）
```

### 导入检查
```bash
python -c "from llm_client import call_llm; from prompt_tuner import train_prompt; print('✓ All imports OK')"
# 输出：✓ All imports OK
```

### CLI 参数检查
```bash
python paper_extraction.py --help | grep -c "model"
# 应该输出：1（表示 --model 参数存在）
```

## 📖 新增文档文件

### 1. PARAMETERIZATION_GUIDE.md（核心用户指南）
- 问题描述和解决方案
- 代码修改详解
- 使用方法（4 个场景）
- 诊断和排查步骤
- 常见问题解答
- 日志格式说明

### 2. CHANGES.md（快速参考）
- 简明的修改日志
- 快速验证步骤

### 3. PHASE7_SUMMARY.md（项目总结）
- 任务完成清单
- 实现要点
- 工作流程
- 关键指标和改进

### 4. QUICKSTART.sh（演示脚本）
- 4 个常用场景的示例命令
- 每个场景都包含注释说明

### 5. diagnose.py（自动诊断工具）
- 分析 `prompt_tuner_trials.jsonl`
- 验证样本展开是否正确
- 检查 LLM 响应是否有效
- 统计各个关键字段的出现次数

## 🚀 使用场景验证

### 场景 1：基本规则抽取
```bash
python paper_extraction.py --template template.json samples/*.md
```
- 预期：使用规则抽取，无需 API
- 验证：`results.csv` 生成成功

### 场景 2：使用 LLM，默认模型
```bash
python paper_extraction.py \
  --template template.json \
  --use-llm \
  samples/*.md
```
- 预期：使用 LLM（默认 deepseek-r1:671b-64k）
- 验证：检查是否读取了环境变量或使用了缓存的 prompt_config.json

### 场景 3：使用 LLM，指定模型
```bash
python paper_extraction.py \
  --template template.json \
  --use-llm \
  --model "gpt-4" \
  samples/*.md
```
- 预期：使用指定的模型（gpt-4）
- 验证：检查 `llm_raw_responses.jsonl` 中记录的模型是否为 gpt-4

### 场景 4：完整流程（Prompt 调优）
```bash
python paper_extraction.py \
  --template template.json \
  --use-llm \
  --train-prompt \
  --dev-labeled samples/labeled.jsonl \
  --model "deepseek-chat" \
  samples/*.md
```
- 预期：运行 200 次 trial，生成最佳配置
- 验证步骤：
  1. `prompt_tuner_trials.jsonl` 包含 200 条记录
  2. `python diagnose.py` 显示 sample_expanded_prompt_len > 0
  3. `python diagnose.py` 显示 avg_score > 0 的 trial 数量 > 0
  4. `prompt_config.json` 包含最佳配置

## 📊 Trial 日志验证

### 记录示例
```json
{
  "trial": 0,
  "prompt_template": "Extract material properties...",
  "model_params": {"model": "deepseek-chat", "temperature": 0.0},
  "avg_score": 0.1,
  "sample_expanded_prompt_len": 1234,
  "sample_llm_response": "[{\"material\":\"Al\",\"property\":\"density\",\"value\":\"2.78\"}]",
  "sample_llm_error": null
}
```

### 字段检查清单
- [x] `trial`：整数，从 0 到 trials-1
- [x] `prompt_template`：字符串，包含 {{content}} 和/或 {{filename}}
- [x] `model_params`：对象，包含 model 和 temperature
- [x] `avg_score`：浮点数，0.0 到 1.0 之间
- [x] `sample_expanded_prompt_len`：整数，展开后 prompt 的字符数
- [x] `sample_llm_response`：字符串或 null，LLM 返回的前 200 字符
- [x] `sample_llm_error`：字符串或 null，错误信息（前 100 字符）
- [x] `sample_expand_error`：字符串或 null，展开错误（如有）

## ⚠️ 已知限制和说明

1. **Trial 日志只记录第一个样本**
   - 原因：完整日志可能过大，影响性能
   - 目的：诊断 {{content}} 展开和 LLM 响应
   - 如需完整日志，可修改代码去掉 `dev[:1]` 限制

2. **sample_llm_response 截断到 200 字符**
   - 原因：保持日志文件大小合理
   - 好处：仍足以诊断是否返回了有效 JSON
   - 完整响应存储在 `llm_raw_responses.jsonl`（如启用）

3. **温度参数随机采样**
   - 当前：从 [0.0, 0.2, 0.5] 中随机选择
   - 目的：探索 temperature 对质量的影响
   - 可修改 `prompt_tuner.py` 第 ~73 行调整范围

## 🎓 学习资源

- **快速上手**：阅读 PARAMETERIZATION_GUIDE.md 的"使用方法"部分
- **故障排查**：使用 `diagnose.py` 脚本或参考"诊断和排查"部分
- **深入理解**：阅读 CHANGES.md 和代码注释
- **示例命令**：参考 QUICKSTART.sh

## ✨ 亮点改进

### 之前的困境
- ❌ Model name 硬编码，用户无法更改
- ❌ Trial 日志只有一个数字 (score)，无法诊断问题
- ❌ avg_score=0 时，用户无从下手

### 现在的能力
- ✅ `--model` 参数支持任意模型名称
- ✅ Trial 日志包含 prompt 长度、LLM 响应、错误信息
- ✅ 使用 `diagnose.py` 快速定位问题
- ✅ 白盒式诊断，每一步都能看到中间结果

## 📝 下一步建议

### 短期（立即可做）
1. 运行诊断脚本验证当前数据
   ```bash
   python diagnose.py prompt_tuner_trials.jsonl
   ```

2. 查看完整的 trial 日志格式
   ```bash
   head -1 prompt_tuner_trials.jsonl | python -m json.tool
   ```

### 中期（需要用户参与）
1. 根据诊断结果调整 prompt template
2. 尝试不同的模型和参数组合
3. 收集更多标注数据以提高评估准确性

### 长期（可选增强）
1. 支持更多的超参数搜索范围
2. 集成贝叶斯优化而不是随机搜索
3. 支持多个开发集的加权评估
4. 与 agentlightning 的算法框架深度集成

---

**状态**：✅ **Phase 7 完成**

所有任务已完成，代码已验证，文档已就绪。

