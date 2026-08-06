# -*- coding: utf-8 -*-
"""
第 8 章配套: 一个最小 MCP 工具服务器(stdio 传输)
暴露两个工具: add(加法) / calc(四则运算表达式)
任何支持 MCP 的客户端都能通过协议发现并调用它们, 无需单独写对接代码
被 mcp_skills_demo.py 以子进程方式启动; 也可独立调试: python mcp_server.py
依赖: pip install mcp
"""
import ast
import operator as op
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo-tools")


@mcp.tool()
def add(a: int, b: int) -> int:
    """两个整数相加"""
    return a + b


_OPS = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
        ast.Div: op.truediv, ast.Pow: op.pow, ast.Mod: op.mod, ast.USub: op.neg}


@mcp.tool()
def calc(expr: str) -> str:
    """计算一个数学表达式, 如 "38*27+100" """
    def ev(node):
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](ev(node.left), ev(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](ev(node.operand))
        raise ValueError("不支持的表达式")
    return str(ev(ast.parse(expr, mode="eval")))


if __name__ == "__main__":
    mcp.run()   # 默认 stdio 传输: 通过标准输入输出与客户端通信
