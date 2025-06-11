import asyncio
import ast
from fastmcp import Client

from openai import OpenAI

import os
from dotenv import load_dotenv

client = Client("test_server.py")

load_dotenv()

async def main():
    async with Client("test_server.py") as client:
        chat = OpenAI()

        tools = await client.list_tools()
        openai_tools = 0

        print(tools)
        openai_tools = []

        it_count = 0

        for tool in tools:
            print("\n")
            print(tool)
            print("\n")

            it_count += 1

            #print(tool.description)

            openai_tool = {
                "type": "function",
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": {

                    },
                    "required": [
                        
                    ],
                    "additionalProperties": False
                }
            }

            i = 0

            for prop in tool.inputSchema["properties"].keys():
                # Creates the keys needed for the property names, also inserts a blank description key
                openai_tool["parameters"]["properties"][tool.inputSchema["required"][i]] = {}
                openai_tool["parameters"]["properties"][tool.inputSchema["required"][i]]["type"] = {}                
                openai_tool["parameters"]["properties"][tool.inputSchema["required"][i]]["description"] = ""
                
                # Sets the type of the parameter with the current name to the correct type
                openai_tool["parameters"]["properties"][tool.inputSchema["required"][i]]["type"] = tool.inputSchema["properties"][prop]["type"]
                
                # Sets the index of the required params list to the name at the current index
                openai_tool["parameters"]["required"].append(tool.inputSchema["required"][i])

                i += 1
            
            openai_tools.append(openai_tool)
                

        """tools = [{
    "type": "function",
    "name": "greet",
    "description": "Greets a user with Hello followed by their name.",
    "parameters": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The name of the person to greet"
            }
        },
        "required": [
            "name"
        ],
        "additionalProperties": False
    }
},
    {
    "type": "function",
    "name": "basic_math",
    "description": "Performs a mathematical operation using two numbers, either adds them together, subtracts the second from the first, multiplies them together, or divides the first by the second. A parameter specifies which operation is used.",
    "parameters": {
        "type": "object",
        "properties": {
            "n1": {
                "type": "number",
                "description": "The first number"
            },
            "n2": {
                "type": "number",
                "description": "The second number"
            },
            "op": {
                "type": "string",
                "description": "The mathematical operation to be done. + for addition, * for multiplication, - for subtraction, or / for division"
            }
        },
        "required": [
            "n1", "n2"
        ],
        "additionalProperties": False
    }
},
    {
    "type": "function",
    "name": "command",
    "description": "Runs a command on a bash terminal with the given arguments.",
    "parameters": {
        "type": "object",
        "properties": {
            "args": {
                "type": "string",
                "description": "The bash command that will be run"
            }
        },
        "required": [
            "args"
        ],
        "additionalProperties": False
    }
}
]"""

        message = input("What would you like to ask?\n")

        response = chat.responses.create(
            model="gpt-4.1",
            input=[{"role": "user", "content": message}],
            tools=openai_tools
        )

        try:
            tool_arguments = response.output[0].arguments
            tool_name = response.output[0].name
            print("Args: " + tool_arguments + "\nName: " + tool_name + "\n")
            await call_tool(tool_name, ast.literal_eval(tool_arguments))
        except:
            print(response)


async def call_tool(function_name: str, vals: dict):
    async with client:
        result = await client.call_tool(function_name, vals)
        print(result)

if __name__ == "__main__":
    asyncio.run(main())