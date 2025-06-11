import asyncio
import ast
from fastmcp import Client

from openai import OpenAI

from dotenv import load_dotenv

client = Client("test_server.py")

load_dotenv()

async def main():
    async with Client("test_server.py") as client:
        chat = OpenAI()

        tools = await client.list_tools()
        openai_tools = 0

        openai_tools = []

        for tool in tools:
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
            
        messages = []
        
        while True:
            message = input("What would you like to ask?\n")

            messages.append({"role": "user", "content": message})

            response = chat.responses.create(
                model="gpt-4o",
                input=messages,
                tools=openai_tools
            )

            print(response.output[0])
        
            try:
                tool_arguments = response.output[0].arguments
                tool_name = response.output[0].name
            
                print("Args: " + tool_arguments + "\nName: " + tool_name + "\n")
            
                tool_result = await call_tool(tool_name, ast.literal_eval(tool_arguments))
            
                tool_call_id = response.output[0].call_id

                messages.append({
                   "role": "assistant",
                   "content": "Called " + tool_name + " tool with arguments: " + response.output[0].arguments
                #"tool_calls": [
                #    {
                #        "id": tool_call_id,
                #        "type": "function",
                #        "function": {
                #            "name": tool_name,
                #            "arguments": str(tool_arguments)
                #        }
                #    }
                #]
                })
            
                messages.append({
                    "role": "system",
                    #"tool_call_id": tool_call_id,
                    #"name": tool_name,
                    "content": "Result of tool call:" + str(tool_result)
                })

                for message in messages:
                    print(message)
                    print("\n")
            
                response = chat.responses.create(
                    model="gpt-4o",
                    input=messages,
                    tools=openai_tools
                )   

                print("\n\n\n")
                #print(response)

                messages.append({"role": "assistant", "content": response.output[0].content[0].text})
            except:
                messages.append({"role": "assistant", "content": response.output[0].content[0].text})
                print("no tool executed")

            print("ChatGPT Response:\n")
            print(response.output[0].content[0].text)



async def call_tool(function_name: str, vals: dict):
    async with client:
        result = await client.call_tool(function_name, vals)
        print(result[0].text)
        return result[0].text

if __name__ == "__main__":
    asyncio.run(main())