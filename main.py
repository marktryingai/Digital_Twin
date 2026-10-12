# ==============================================================================
# FILE: main.py
# ==============================================================================
# WHAT THIS CODE DOES EXACTLY:
# This is the "brain" and user interface of your application. It brings 
# everything together.
# It sets up the Gradio chat window, tracks the chat history, sends the 
# conversation to OpenAI, handles any tools the AI tries to use, runs the 
# secondary "Smart Evaluator" to catch off-topic questions, and finally 
# launches the webpage.
# ==============================================================================

import os
from dotenv import load_dotenv
from openai import OpenAI
import gradio as gr  # Gradio is the library that builds the visual chat interface

# Import the specific pieces we need from our other two files
from context import system_prompt
from tools import tools, handle_tool_calls, record_unknown_question

# Load the secret keys (like OPENAI_API_KEY) from the .env file
load_dotenv(override=True)

# Initialize the OpenAI client so we can talk to the GPT models
openai = OpenAI()

# 1. THE SMART EVALUATOR
# This is a secondary, background AI call. It acts as a strict "judge" to check if the user is asking off-topic questions.
def evaluate_question(message):
    eval_prompt = f"""
    Evaluate this user message: "{message}"
    Is this message asking about a topic unrelated to a professional career, work background, skills, or experience?
    
    RULES:
    - Reply 'NO' if the message is a standard greeting or pleasantry (e.g., "hi", "hello", "how are you").
    - Reply 'NO' if the message is related to professional topics.
    - Reply 'YES' ONLY if the message explicitly asks about unrelated topics (e.g., sports, personal preferences, trivia).
    
    Reply exactly with 'YES' or 'NO'.
    """
    
    # We ask gpt-4o-mini this specific question.
    # temperature=0.0 means the AI will be as logical and robotic as possible (no creative guessing)
    eval_response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": eval_prompt}],
        temperature=0.0
    )
    
    # Extract the YES or NO answer, remove any extra spaces (.strip()), and make it uppercase
    return eval_response.choices[0].message.content.strip().upper()

# 2. THE MAIN CHAT LOGIC
# This function runs every single time the user types a message and hits enter in the Gradio chat window.
def chat(message, history):
    # Start the message list with our giant system prompt (from context.py)
    messages = [{"role": "system", "content": system_prompt}]
    
    # Loop through the past conversation history and add it so the AI remembers what was just said
    for item in history:
        if isinstance(item, dict):
            messages.append(item)
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            messages.append({"role": "user", "content": item[0]})
            messages.append({"role": "assistant", "content": item[1]})
            
    # Add the brand new message the user just typed
    messages.append({"role": "user", "content": message})
    
    # Send the whole conversation to OpenAI to get a reply
    # We pass in 'tools=tools' (from tools.py) so the AI knows it has superpowers it can use
    response = openai.chat.completions.create(
        model="gpt-4o-mini", 
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    response_message = response.choices[0].message
    
    # 3. HANDLE AI TOOL CALLS
    # If the AI decides on its own to use a tool (like recording a user's email)
    if response_message.tool_calls:
        # Add the AI's tool request to the chat history
        messages.append(response_message)
        
        # Run the Python functions in tools.py and get the results
        tool_results = handle_tool_calls(response_message.tool_calls)
        
        # Add the results of the tool back into the conversation
        messages.extend(tool_results)
        
        # Send everything back to OpenAI one more time so it can say "Thanks, I recorded that!"
        second_response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        return second_response.choices[0].message.content
        
    # If no tools were called naturally, grab the text the AI wants to say
    reply_content = response_message.content
    
    # 4. RUN THE SMART EVALUATOR FALLBACK
    # We pass the user's message to our judge function
    evaluation = evaluate_question(message)
    print(f"\n--- DEBUG Evaluator: {evaluation} ---", flush=True)
    
    # If the judge says YES (it is an unrelated question), manually trigger the Pushover tool
    if "YES" in evaluation:
        print("--- DEBUG: Unrelated question detected. Triggering push... ---", flush=True)
        # Call the function from tools.py directly
        record_unknown_question(message)
        
    # Finally, return the text so Gradio can display it in the chat window to the user
    return reply_content

# 5. LAUNCH THE APP
# Get the username and password for the website from the .env file (or use defaults if they aren't there)
app_user = os.getenv("APP_USER", "admin")
app_pass = os.getenv("APP_PASS", "password123")

# Create the Gradio chat interface, tie it to our 'chat' function, and turn it on
gr.ChatInterface(chat).launch(
    server_name="0.0.0.0",  # This makes it accessible over the local network/internet
    inbrowser=True,         # Automatically opens a tab in your web browser
    auth=(app_user, app_pass) # Puts a login screen in front of the chat
)