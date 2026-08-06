# -*- coding: utf-8 -*-
"""
第 8 章: 工具从哪来, 怎么批量接进来? —— MCP 协议调用 + Skill 流程执行
输入: 无(内置演示)
输出: 1) 通过 MCP 协议发现工具列表  2) 调用 add / calc 的结果
      3) Skill 演示: 读取 SKILL.md 操作手册, 按步骤执行配套脚本
运行: python mcp_skills_demo.py
依赖: pip install mcp
结构: mcp_server.py 为本脚本启动的 MCP 服务器(同目录)
      skills/expense_report/ 为一个 skill 示例(SKILL.md + scripts/fill.py)
"""
import asyncio
import subprocess
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = Path(__file__).parent


async def mcp_demo():
    """启动 MCP 服务器(子进程), 通过协议发现工具并调用"""
    params = StdioServerParameters(
        command=sys.executable,
        args=[str(HERE / "mcp_server.py")],
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1) 发现: 不问不知道, 一问全知道
            tools = await session.list_tools()
            print("=== MCP 发现到的工具 ===")
            for t in tools.tools:
                print(f"  {t.name}: {t.description}")

            # 2) 调用: 按协议传名称和参数, 结果原样返回
            r1 = await session.call_tool("add", {"a": 38, "b": 27})
            print(f"\nadd(38, 27) -> {r1.content[0].text}")

            r2 = await session.call_tool("calc", {"expr": "38*27+100"})
            print(f"calc('38*27+100') -> {r2.content[0].text}")


def skill_demo():
    """演示 Skill: AI 遇到对应任务时, 加载"操作手册"并按流程执行"""
    skill_dir = HERE / "skills" / "expense_report"
    manual = skill_dir / "SKILL.md"
    print("\n=== Skill 演示: 加载操作手册 ===")
    text = manual.read_text(encoding="utf-8")
    print(f"已加载 {manual.name}, 共 {len(text)} 字; 手册开头:")
    print("\n".join(text.splitlines()[:8]))

    print("\n=== 按手册第 2 步, 执行配套脚本 scripts/fill.py ===")
    script = skill_dir / "scripts" / "fill.py"
    result = subprocess.run([sys.executable, str(script)],
                            capture_output=True, text=True, cwd=str(skill_dir))
    print(result.stdout)
    if result.returncode != 0:
        print("脚本执行出错:", result.stderr, file=sys.stderr)


def main():
    asyncio.run(mcp_demo())
    skill_demo()


if __name__ == "__main__":
    main()
