import asyncio
import ast
from fastmcp import Client
from flask import Flask, request
from flask_cors import CORS
import psycopg2
import requests
import logging

from openai import OpenAI

from dotenv import load_dotenv

chat = OpenAI()

client = Client("test_server.py")

load_dotenv()

logging.basicConfig(
    level=logging.INFO,  # or logging.DEBUG
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("server.log", mode="a"),
        logging.StreamHandler()  # Optional: logs to console too
    ]
)

messages = []

openai_tools = None

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
        
        response = {}
        prev_resp_id = None

        while True:
            message = input("What would you like to ask?\n") # Switch to 

            messages.append({"role": "user", "content": message})

            response = chat.responses.create(
                model="gpt-4o",
                input=messages,
                tools=openai_tools,
                previous_response_id=prev_resp_id
            )

            # print(response.output[0])
        
            try:
                tool_arguments = response.output[0].arguments
                tool_name = response.output[0].name
            
                print("Args: " + tool_arguments + "\nName: " + tool_name + "\n")
            
                tool_result = await call_tool(tool_name, ast.literal_eval(tool_arguments))
            
                tool_call_id = response.output[0].call_id
                prev_resp_id = response.id

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

                #print("\n\n\n")
                #print(response)

                messages.append({"role": "assistant", "content": response.output[0].content[0].text})
            except:
                messages.append({"role": "assistant", "content": response.output[0].content[0].text})
                print("no tool executed")

            print("ChatGPT Response:\n")
            print(response.output[0].content[0].text)
            prev_resp_id = response.id

async def get_openai_tools():
    async with Client("test_server.py") as client:
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
                    "properties": {},
                        "required": [],
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

        return openai_tools


async def handle_message(message):
    global openai_tools

    app.logger.info(f"{request.method} {request.path} - Starting message generation")

    if openai_tools == None:
        openai_tools = await get_openai_tools()

    app.logger.info(f"{request.method} {request.path} - Successfully retrieved MCP tools list")

    response = {}
    prev_resp_id = None

    app.logger.info(f"{request.method} {request.path} - Sending LLM message: {message}")
  
    messages.append({"role": "user", "content": message})

    response = chat.responses.create(
        model="gpt-4o",
        input=messages,
        tools=openai_tools,
        previous_response_id=prev_resp_id
    )

    #print(response.output[0])
    
    app.logger.info(f"{request.method} {request.path} - ChatGPT response generated")

    try:
        app.logger.info(f"{request.method} {request.path} - Tool call detected.")
    
        tool_arguments = response.output[0].arguments
        tool_name = response.output[0].name
            
        #print("Args: " + tool_arguments + "\nName: " + tool_name + "\n")
        
        app.logger.info(f"{request.method} {request.path} - Calling tool: {tool_name}")

        tool_result = await call_tool(tool_name, ast.literal_eval(tool_arguments))
            
        app.logger.info(f"{request.method} {request.path} - Received tool result")

        tool_call_id = response.output[0].call_id
        prev_resp_id = response.id

        app.logger.info(f"{request.method} {request.path} - Adding llm tool call to messages")

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
            
        app.logger.info(f"{request.method} {request.path} - Creating additional llm message using tool result")
        
        response = chat.responses.create(
            model="gpt-4o",
            input=messages,
            tools=openai_tools
        )   

        #print("\n\n\n")
        #print(response)

        app.logger.info(f"{request.method} {request.path} - Adding final message to messages")

        messages.append({"role": "assistant", "content": response.output[0].content[0].text})
    except:
        app.logger.info(f"{request.method} {request.path} - No tool call, responding to llm message")

        messages.append({"role": "assistant", "content": response.output[0].content[0].text})
        #print("no tool executed")

    #print("ChatGPT Response:\n")
    #print(response.output[0].content[0].text)

    prev_resp_id = response.id

    app.logger.info(f"{request.method} {request.path} - Returning final llm message: {response.output[0].content[0].text}")
    return response.output[0].content[0].text


async def call_tool(function_name: str, vals: dict):
    async with Client("test_server.py") as client:
        result = await client.call_tool(function_name, vals)
        #print(result[0].text)
        return result[0].text

app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:5500"])

@app.before_request
def log_request_info():
    app.logger.info(f"{request.method} {request.path} - {request.remote_addr}")

@app.route('/receive_text', methods=['POST'])
def receive_text():
    """
    Receives text data from a client via a POST request.
    It expects the text data directly in the request body.
    """

    app.logger.info(f"{request.method} {request.path} - Body Text Recieved: {request.data.decode('utf-8')}")
    # request.data contains the raw incoming request body as bytes
    received_data = request.data.decode('utf-8') # Decode bytes to a UTF-8 string

    #print(f"Server received text: {received_data}")

    llm_message = asyncio.run(handle_message(received_data))

    app.logger.info(f"{request.method} {request.path} - Returning Message: {llm_message}")
    # Send a simple confirmation back to the client
    return llm_message, 200

@app.route('/get_username', methods=["POST"])
def get_username():
    user_id = request.data.decode('utf-8')

    conn = psycopg2.connect(
        dbname="vectordb",
        user="brettpaden",
        password="example",
        host="127.0.0.1",
        port="5432"
    )

    cur = conn.cursor()

    cur.execute("""
        SELECT name FROM avatars WHERE uuid = %s;
    """, (user_id,))
    
    result = cur.fetchone()

    conn.commit()
    cur.close()

    return str(result[0]), 200

@app.route('/get_key', methods=["POST"])
def get_key():
    user_id = request.data.decode('utf-8')

    conn = psycopg2.connect(
        dbname="vectordb",
        user="brettpaden",
        password="example",
        host="127.0.0.1",
        port="5432"
    )

    cur = conn.cursor()

    cur.execute("""
        SELECT heygen_key FROM avatars WHERE uuid = %s;
    """, (user_id,))
    
    result = cur.fetchone()

    conn.commit()
    cur.close()

    return str(result[0]), 200

@app.route('/get_session_token', methods=["POST"])
def get_session_token():
    app.logger.info(f"{request.method} {request.path} - User UUID: {request.data.decode('utf-8')}")
    user_id = request.data.decode('utf-8')

    conn = psycopg2.connect(
        dbname="vectordb",
        user="brettpaden",
        password="example",
        host="127.0.0.1",
        port="5432"
    )

    cur = conn.cursor()

    app.logger.info(f"{request.method} {request.path} - Successfully connected to Postgres database")

    cur.execute("""
        SELECT heygen_key, name FROM avatars WHERE uuid = %s;
    """, (user_id,))
    
    result = cur.fetchone()

    conn.commit()
    cur.close()

    api_key = str(result[0])
    botName = str(result[1])

    app.logger.info(f"{request.method} {request.path} - Received HeyGen api key: {str(result[0])}")
    app.logger.info(f"{request.method} {request.path} - Received name: {str(result[1])}")

    #print("Api key = " + api_key +"\n")

    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": api_key,
    }

    response = requests.post("https://api.heygen.com/v1/streaming.create_token", headers=headers, data=None)

    app.logger.info(f"{request.method} {request.path} - Generating session token with api key: {str(result[0])}")
    
    session_token = response.json()["data"]["token"]

    app.logger.info(f"{request.method} {request.path} - Created session token: {session_token}")

    # print(session_token)

    app.logger.info(f"{request.method} {request.path} - Returning 200 with session token: {session_token}")
    return {
        "session_token": str(session_token),
        "bot_name": botName
    }, 200




if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9876)
    