# 📚 Phase 7 文档和工具索引

## 快速导航

| 文件名 | 类型 | 长度 | 用途 | 推荐阅读 |
|--------|------|------|------|--------|
| **QUICK_REFERENCE.md** | 📋 速查表 | 3KB | 常用命令、快速查询 | ⭐⭐ 首先看这个 |
| **PARAMETERIZATION_GUIDE.md** | 📖 完整指南 | 20KB | 详细的问题描述、使用方法、诊断步骤 | ⭐⭐⭐⭐ 想深入理解 |
| **EXECUTIVE_SUMMARY.md** | 📊 执行总结 | 15KB | 高层总结、数据流、改进指标 | ⭐⭐⭐ 想快速了解 |
| **WORK_COMPLETED.md** | ✅ 完成报告 | 12KB | 工作清单、验证状态、交付物 | ⭐⭐⭐ 项目总结 |
| **CHANGES.md** | 📝 修改日志 | 5KB | 简洁的改动记录、验证步骤 | ⭐⭐ 看具体改了什么 |
| **PHASE7_SUMMARY.md** | 📋 项目总结 | 10KB | 任务目标、实现清单、关键指标 | ⭐⭐⭐ 学习项目细节 |
| **CHECKLIST.md** | ✓ 验收清单 | 10KB | 验证步骤、测试状态、使用场景 | ⭐⭐ 验证功能 |
| **diagnose.py** | 🔧 工具 | 2KB | 自动诊断脚本，分析 trials.jsonl | ⭐⭐⭐⭐ 必用工具 |
| **QUICKSTART.sh** | 🚀 示例 | 1KB | 4 个常用场景的示例命令 | ⭐⭐⭐ 学习用法 |

---

## 按使用场景推荐阅读

### 🏃 **场景 1：我只有 5 分钟**
1. **QUICK_REFERENCE.md** - 快速命令参考
2. 运行一个命令，尝试 `--model` 参数
3. 完成！

### 🚶 **场景 2：我有 30 分钟** 
1. **QUICK_REFERENCE.md** - 了解基本用法（5 分钟）
2. **PARAMETERIZATION_GUIDE.md** - 阅读"问题描述"和"使用方法"部分（15 分钟）
3. **QUICKSTART.sh** - 看 4 个示例命令（5 分钟）
4. 运行一个示例，体验新功能（5 分钟）

### 🚴 **场景 3：我有 1 小时**
1. **EXECUTIVE_SUMMARY.md** - 了解总体改进（10 分钟）
2. **PARAMETERIZATION_GUIDE.md** - 完整阅读（30 分钟）
3. 查看修改后的代码：`paper_extraction.py`、`prompt_tuner.py`（10 分钟）
4. 运行 `--train-prompt` 完整流程（10 分钟）

### 🎓 **场景 4：我想深度掌握**
1. 按顺序阅读所有文档：
   - QUICK_REFERENCE.md（速查）
   - PARAMETERIZATION_GUIDE.md（完整指南）
   - EXECUTIVE_SUMMARY.md（数据流分析）
   - WORK_COMPLETED.md（工作报告）
   - PHASE7_SUMMARY.md（项目细节）
   - CHECKLIST.md（验证清单）
2. 研究修改后的代码
3. 运行完整的 `--train-prompt` 流程
4. 手动检查 `prompt_tuner_trials.jsonl` 和 `prompt_config.json`

---

## 按问题类型推荐查看

### ❓ "如何使用 --model 参数？"
- **QUICK_REFERENCE.md** → "常用命令"部分
- **PARAMETERIZATION_GUIDE.md** → "使用方法"部分

### ❓ "为什么 avg_score 都是 0？"
- **PARAMETERIZATION_GUIDE.md** → "诊断和排查"部分
- 运行 **diagnose.py** 脚本查看诊断结果

### ❓ "修改了什么代码？"
- **CHANGES.md** → 简洁的修改记录
- **PARAMETERIZATION_GUIDE.md** → "代码修改详情"部分
- 查看 `paper_extraction.py` 和 `prompt_tuner.py` 源代码

### ❓ "Trial 日志中新增了哪些字段？"
- **PARAMETERIZATION_GUIDE.md** → "日志文件格式"部分
- **QUICK_REFERENCE.md** → "Trail 日志字段"表格

### ❓ "有什么示例命令？"
- **QUICKSTART.sh** → 4 个常用场景
- **QUICK_REFERENCE.md** → "常用命令"部分
- **PARAMETERIZATION_GUIDE.md** → "使用方法"部分

### ❓ "如何诊断问题？"
- 运行 **diagnose.py** 脚本（最简单）
- **PARAMETERIZATION_GUIDE.md** → "诊断和排查"部分（详细步骤）

### ❓ "代码是否有语法错误？"
- **CHECKLIST.md** → "语法检查"部分
- 或运行：`python -m py_compile paper_extraction.py prompt_tuner.py`

---

## 文件内容速览

### 📋 QUICK_REFERENCE.md
**内容**：
- 快速参考卡片（只有 15KB，最精简）
- 常用命令、Trial 日志字段、常见问题
- 使用场景决策树

**何时看**：需要快速查阅时（5 分钟内找到答案）

### 📖 PARAMETERIZATION_GUIDE.md
**内容**：
- 完整的问题描述和解决方案
- 代码修改的详细说明
- 4 个使用场景的完整示例
- 7 个诊断和排查步骤
- 3 个常见问题解答

**何时看**：想全面理解问题和解决方案时

### 📊 EXECUTIVE_SUMMARY.md
**内容**：
- 高层执行总结（适合决策者）
- 问题解决详解（对比改前改后）
- 数据流图解
- 关键改进指标表
- 亮点总结

**何时看**：想快速了解改进了什么、为什么改、改了什么

### ✅ WORK_COMPLETED.md
**内容**：
- 任务回顾和问题分析
- 完成的工作清单（代码 + 文档 + 工具）
- 关键改进详解（3 个问题 → 3 个解决）
- 生产使用场景
- 后续建议

**何时看**：项目管理视角，看整体工作和后续方向

### 📝 CHANGES.md
**内容**：
- 修改内容简表
- 为什么要做这些修改
- 快速验证步骤

**何时看**：只想看代码改了什么，不想看原理

### 📋 PHASE7_SUMMARY.md
**内容**：
- 完成清单
- 实现要点
- 工作流程
- 关键指标和改进
- 学习资源导航

**何时看**：想看项目总结和学习资源

### ✓ CHECKLIST.md
**内容**：
- 完成的任务清单
- 测试状态和验证步骤
- 新增文档和工具说明
- 已知限制和说明
- 下一步建议

**何时看**：验证功能是否完整、想确认代码质量

### 🔧 diagnose.py
**内容**：
- 自动诊断脚本（可独立运行）
- 分析 `prompt_tuner_trials.jsonl`
- 检查样本展开、LLM 响应、错误信息
- 显示诊断结果和建议

**何时用**：运行 `--train-prompt` 后，快速诊断结果

### 🚀 QUICKSTART.sh
**内容**：
- 4 个常用场景的示例命令
- 每个场景都有注释说明
- 可直接复制粘贴或运行 bash 脚本

**何时用**：学习如何使用新功能

---

## 阅读路径流程图

```
┌─────────────────────────┐
│  我想快速上手（5 分钟）   │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ 1. 读 QUICK_REFERENCE.md（2 分钟）  │
│ 2. 复制一个命令，运行（2 分钟）      │
│ 3. 运行 diagnose.py（1 分钟）       │
└──────────┬──────────────────────────┘
           │
           ▼
        完成！


┌──────────────────────────┐
│ 我想标准学习（30 分钟）   │
└──────────┬───────────────┘
           │
           ▼
┌────────────────────────────────────┐
│ 1. QUICK_REFERENCE.md（5 分钟）   │
│ 2. PARAMETERIZATION_GUIDE.md       │
│    - 问题描述（5 分钟）            │
│    - 代码修改（5 分钟）            │
│    - 使用方法（10 分钟）           │
│ 3. 运行一个示例（5 分钟）          │
└──────────┬───────────────────────────┘
           │
           ▼
     掌握了！


┌──────────────────────────┐
│ 我想深度理解（1-2 小时）  │
└──────────┬───────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│ 阅读顺序：                          │
│ 1. QUICK_REFERENCE.md（10 分钟）   │
│ 2. EXECUTIVE_SUMMARY.md（20 分钟）  │
│ 3. PARAMETERIZATION_GUIDE.md        │
│    （30 分钟）                      │
│ 4. 查看源代码（15 分钟）            │
│ 5. 运行 --train-prompt（20 分钟）  │
│ 6. 手动检查日志和配置（15 分钟）    │
└──────────┬───────────────────────────┘
           │
           ▼
     完全掌握！
```

---

## 📁 目录树

```
examples/paperexaction/
├── 核心脚本
│   ├── paper_extraction.py        ✏️ 修改：添加 --model 参数
│   ├── prompt_tuner.py            ✏️ 修改：添加诊断日志
│   └── llm_client.py              ✓ 无需修改
│
├── 新增诊断和示例
│   ├── diagnose.py                ✨ 新增：诊断工具
│   └── QUICKSTART.sh              ✨ 新增：示例脚本
│
├── 📚 完整文档（新增）
│   ├── QUICK_REFERENCE.md         ⭐ 速查表（首先看）
│   ├── PARAMETERIZATION_GUIDE.md  ⭐⭐⭐⭐ 完整指南
│   ├── EXECUTIVE_SUMMARY.md       ⭐⭐⭐ 执行总结
│   ├── WORK_COMPLETED.md          ✅ 完成报告
│   ├── CHANGES.md                 📝 修改日志
│   ├── PHASE7_SUMMARY.md          📋 项目总结
│   ├── CHECKLIST.md               ✓ 验收清单
│   └── WORK_COMPLETED.md          📚 本索引文件
│
└── 数据和配置
    ├── samples/                   📂 样本文件
    ├── labeled.jsonl              📄 标注数据
    ├── template.json              ⚙️ 配置模板
    ├── prompt_config.json         💾 最佳配置
    └── prompt_tuner_trials.jsonl  📊 Trial 日志
```

---

## 🎓 学习建议

1. **第一次接触**：只读 QUICK_REFERENCE.md 的"常用命令"部分
2. **想深入理解**：读完整的 PARAMETERIZATION_GUIDE.md
3. **想了解项目**：读 EXECUTIVE_SUMMARY.md 或 WORK_COMPLETED.md
4. **想查快速问题**：用 QUICK_REFERENCE.md 的速查表
5. **想诊断结果**：运行 diagnose.py 脚本
6. **想看代码变更**：读 CHANGES.md 或查看源代码

---

**最后修改时间**：Phase 7 完成  
**总文档数**：9 个（8 个 markdown + 1 个 Python 工具）  
**总文档字数**：约 3000+ 字  
**推荐首先阅读**：QUICK_REFERENCE.md

