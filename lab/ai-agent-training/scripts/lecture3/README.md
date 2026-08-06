# 附录脚本：把 PPT 每一章亲手跑一遍

配套幻灯片《ChatGPT 是怎么工作的：从"接话机器"到"会干活的助手"》。

## 环境准备

```bash
# Python 3.12+，纯 CPU 即可
pip install torch transformers sentence-transformers mcp fastapi uvicorn
```

模型首次运行自动下载（Qwen2.5-0.5B 系列约 1.5GB，BGE 向量模型约 100MB）。
国内网络可取消每个脚本顶部 `HF_ENDPOINT = "https://hf-mirror.com"` 一行的注释。

## 脚本清单

| # | 脚本 | 章节 | 运行 | 演示内容 |
|---|------|------|------|----------|
| 1 | `tokenizer_demo.py` | 1 | `python tokenizer_demo.py "今天天气真"` | token 切分列表、数量、半句续写 |
| 2 | `training_stages_demo.py` | 2 | `python training_stages_demo.py "怎么煮咖啡?"` | base 续写 vs instruct 问答 |
| 3 | `chat_context_demo.py` | 3 | `python chat_context_demo.py` | 6 轮历史拼接、模板渲染、超长截断（system 保留） |
| 4 | `sampling_demo.py` | 4 | `python sampling_demo.py` | temperature=0 与 0.9 各生成 3 次对比 |
| 5 | `cot_demo.py` | 5 | `python cot_demo.py` | 直接答 vs "请一步一步思考" |
| 6 | `rag_demo.py` | 6 | `python rag_demo.py "出差住宿报销上限是多少?"` | 切块→向量化→Top-2 检索→拼上下文→回答 |
| 7 | `agent_tool_demo.py` | 7 | `python agent_tool_demo.py "38乘27再加100是多少?"` | calc/date 工具 + ReAct 循环（上限 5 轮） |
| 8 | `mcp_skills_demo.py` | 8 | `python mcp_skills_demo.py` | MCP 协议发现/调用工具 + skill 手册流程执行 |
| 9 | `api_server.py` | 9 | `python api_server.py` | 本地 Chat Completions 兼容服务（SSE 流式） |

## 目录结构

```
scripts/
├── tokenizer_demo.py        # 第1章
├── training_stages_demo.py  # 第2章
├── chat_context_demo.py     # 第3章
├── sampling_demo.py         # 第4章
├── cot_demo.py              # 第5章
├── rag_demo.py              # 第6章
├── agent_tool_demo.py       # 第7章
├── mcp_server.py            # 第8章: MCP 工具服务器(被 demo 启动)
├── mcp_skills_demo.py       # 第8章: MCP 客户端 + skill 演示
├── api_server.py            # 第9章
└── skills/
    └── expense_report/      # 第8章 skill 示例
        ├── SKILL.md         # 操作手册: 整理报销的流程与注意事项
        └── scripts/fill.py  # 配套脚本: 分类汇总并生成 报销单.csv
```

## 第 9 章服务调用示例

```bash
# 非流式
curl http://127.0.0.1:8000/v1/chat/completions -H "Content-Type: application/json" \
  -d "{\"model\":\"qwen\",\"messages\":[{\"role\":\"user\",\"content\":\"你好\"}]}"

# 流式(SSE 逐字返回)
curl http://127.0.0.1:8000/v1/chat/completions -H "Content-Type: application/json" \
  -d "{\"model\":\"qwen\",\"messages\":[{\"role\":\"user\",\"content\":\"你好\"}],\"stream\":true}"
```

## 备注

- 0.5B 小模型旨在演示**机制**，生成质量有限；把脚本中的 `MODEL` 换成
  `Qwen/Qwen2.5-1.5B-Instruct` 或更大，效果会明显变好（CPU 仍可跑，只是更慢）。
- 第 5 章 CoT、第 7 章 ReAct 对模型遵循格式的能力较敏感，小模型可能需要多试一两次。
- 所有脚本均为教学用途的最小实现，未做生产级加固。
