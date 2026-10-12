# ==============================================================================
# FILE: tools.py
# ==============================================================================
# WHAT THIS CODE DOES EXACTLY:
# This file manages all of the "tools" (actions) your AI can take. 
# It loads your secret keys from the .env file, talks to the Pushover API to 
# send push notifications to your phone, and provides the exact JSON structures 
# that OpenAI needs to understand what these tools do.
# ==============================================================================

import json
import os
import requests  # This library lets Python send HTTP requests over the internet (like talking to APIs)
from dotenv import load_dotenv

# Load the secret variables from your .env file into this script
load_dotenv(override=True)

# Grab the specific Pushover keys you saved in your .env file
pushover_user = os.getenv("PUSHOVER_USER_KEY")
pushover_token = os.getenv("PUSHOVER_APP_TOKEN")

# This is the official web address for the Pushover API that receives our messages
pushover_url = "https://api.pushover.net/1/messages.json"

# 1. THE MAIN PUSH FUNCTION
# This function takes a piece of text and sends it to your phone via Pushover
def push(text):
    # Print statements to help you debug in the VS Code terminal
    print(f"--- DEBUG Push Text: {text} ---", flush=True)
    print(f"--- DEBUG User Key: {pushover_user} ---", flush=True)
    print(f"--- DEBUG App Token: {pushover_token} ---", flush=True)
    
    # Only try to send the message if both keys successfully loaded from the .env file
    if pushover_user and pushover_token:
        # Use the requests library to send a POST request to Pushover with your keys and the message
        response = requests.post(
            pushover_url,
            data={
                "token": pushover_token,
                "user": pushover_user,
                "message": text,
            },
        )
        # Print Pushover's response (usually says "status": 1 if successful)
        print(f"--- DEBUG Pushover API Response: {response.text} ---\n", flush=True)
    else:
        print("--- DEBUG FAILED: One or both Pushover keys are missing! ---\n", flush=True)

# 2. THE PYTHON TOOLS
# These are the actual Python functions that run when the AI decides to use a tool.
# They both just format a specific message and pass it into the push() function above.
def record_user_details(email, name="Name not provided", notes="not provided"):
    push(f"Recording interest from {name} with email {email} and notes {notes}")
    return "OK"

def record_unknown_question(question):
    push(f"Recording '{question}' asked that I couldn't answer")
    return "OK"

# 3. THE JSON SCHEMAS
# OpenAI's AI cannot read raw Python code. We have to describe our Python functions to the AI using JSON formats.
# This tells the AI the name of the tool, what it does, and what pieces of information (parameters) it needs to collect from the user.
record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "The email address of this user"},
            "name": {"type": "string", "description": "The user's name, if they provided it"},
            "notes": {
                "type": "string",
                "description": "Any additional info about the conversation that's worth recording to give context",
            },
        },
        # We tell the AI that an email is absolutely required to use this tool
        "required": ["email"],
        "additionalProperties": False,
    },
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "The question that couldn't be answered"},
        },
        "required": ["question"],
        "additionalProperties": False,
    },
}

# Group the JSON schemas into a list so we can easily hand them to OpenAI in app.py
tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json},
]

# 4. THE TOOL HANDLER
# When the AI decides it wants to use a tool, it sends back a "tool_call". 
# This function takes that request, finds the matching Python function, and runs it.
def handle_tool_calls(tool_calls):
    results = []
    # Sometimes the AI asks to use multiple tools at once, so we loop through all of them
    for tool_call in tool_calls:
        # Get the name of the tool the AI wants to use (e.g., "record_unknown_question")
        tool_name = tool_call.function.name
        # Get the arguments the AI extracted from the chat (e.g., the actual question asked)
        arguments = json.loads(tool_call.function.arguments)
        
        print(f"Tool called: {tool_name}", flush=True)
        
        # globals().get(tool_name) finds the Python function in this file that has the exact same name
        tool = globals().get(tool_name)
        
        # If the tool exists, run it and pass in the arguments. Otherwise, return an error string.
        result = tool(**arguments) if tool else "No tool found"
        
        # Record the result so we can send it back to the AI, proving the tool actually ran
        results.append(
            {"role": "tool", "content": json.dumps(result), "tool_call_id": tool_call.id}
        )
    return results