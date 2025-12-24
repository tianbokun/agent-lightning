示例：从论文/专利的 Markdown 文件中抽取材料实体及其性质

简介
- 这个示例演示一个轻量级、基于规则的管道，用于从若干 Markdown（`.md`）文件中抽取“材料实体”及其对应的性质（如密度、熔点、电导率等），并输出结构化表格（CSV/JSON）。

设计目标
- 输入：Markdown 文件列表 + 数据模板（JSON），模板中列出要抽取的“性质术语”。
- 输出：每一行对应一个提取到的关系：文件、材料、性质、值、所在句子。
- 实现：仅使用 Python 标准库的轻量级规则与正则（便于在受限环境中运行）。

快速开始
1. 进入示例目录：

```bash
cd examples/paperexaction
```

2. 使用模板和示例 md 文件运行：

```bash
python paper_extraction.py --template template.json --out results.csv samples/sample1.md samples/sample2.md
```

输出文件 `results.csv` 会包含结构化的提取结果。

当你需要更强的抽取能力时，可替换为基于模型的方法（例如调用 LLM/NER 模型），或将本示例作为规则/快速验证步骤。

文件
- [examples/paperexaction/paper_extraction.py](examples/paperexaction/paper_extraction.py)
- [examples/paperexaction/extractor.py](examples/paperexaction/extractor.py)
- [examples/paperexaction/template.json](examples/paperexaction/template.json)
- [examples/paperexaction/samples/sample1.md](examples/paperexaction/samples/sample1.md)
- [examples/paperexaction/samples/sample2.md](examples/paperexaction/samples/sample2.md)

许可证与注意事项
- 此示例为演示用途，规则匹配为启发式方法，不能覆盖所有书写变体。建议在真实项目中增加更多测试样本并使用统计或模型方法进行增强。
