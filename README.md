# This is an incredibly basic mcp server with three commands:

## basic_math:
Enables simple 2 number mathematical functions (+, -, *, /)

## greet:
Greets a given user with "Hello {user}"

## command:
Executes a command on the command line (super insecure)

## Instructions

Make sure to make a virtual environment, set it as your source


Next install dependencies from pyproject.toml using
 
    run python -m pip install

Set your OPENAI_API_KEY in a .env file, then run the test_server.py using

    fastmcp run test_server.py:mcp

Then run test_client.py
