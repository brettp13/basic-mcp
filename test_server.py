import asyncio
from fastmcp import FastMCP, Client
import subprocess

mcp = FastMCP("My MCP Server")

@mcp.tool(description="Greets a user with \"Hello\" followed by their name. This description will be visible to clients. Args: name (str): The name of the person to greet")
def greet(name: str) -> str:
    return f"Hello, {name}!"

@mcp.tool(description="Runs a shell command on the server's operating system. Use with extreme caution, as this can be a security risk if not properly restricted. Args: args (str): The bash command string to execute.")
def command(args: str):
    return subprocess.run(args.split(), capture_output=True, text=True)

@mcp.tool(description="Performs a mathematical operation (addition, subtraction, multiplication, or division) on two numbers. Args: n1 (float): The first number. n2 (float): The second number. op (str): The mathematical operation to be done. Use '+' for addition, '-' for subtraction, '*' for multiplication, or '/' for division.")
def basic_math(n1: float, n2: float, op: str):
    if op == "*":
        return n1 * n2
    elif op == "/":
        return n1 / n2
    elif op == "+":
        return n1 + n2
    elif op == "-":
        return n1 - n2
    return 0

if __name__ == "__main__":
    mcp.run()