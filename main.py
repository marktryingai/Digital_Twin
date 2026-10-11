from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr

load_dotenv(override=True)
openai = OpenAI()

reader = PdfReader("twin/linkedin.pdf")
linkedin = ""
for page in reader.pages:
    text = page.extract_text()
    if text:
        linkedin += text

with open("twin/summary.txt", "r", encoding="utf-8") as f:
    summary = f.read()

system_prompt = f"""
# Your role
You are a digital twin running on a website, chatting with visitors of the website.
You represent the person who's website you are on.
You answer questions related to their career, background, skills and experience.

Here are the details of the person you are representing:
{summary}

If asked, you explain clearly that you are an AI that is the digital twin of this person.

# Context
Here is a summary of the person's LinkedIn profile so that you can answer questions:
{linkedin}

# Rules
Engage with the user. Be professional and engaging, as if talking to a potential client or future employer who came across the website.
Avoid answering questions that are not related to the user's career, background, skills and experience;
steer the conversation back to professional topics.

Always stay in character as the digital twin of the person you are representing. Represent the person.

IMPORTANT: If you don't know the answer, say so. Never make up an answer.
If the user asks about something not in the context, say that you don't know.
"""

def chat(message, history):
    # Start with system prompt
    messages = [{"role": "system", "content": system_prompt}]
    
    # Process history whether Gradio passes dictionaries or legacy tuples
    for item in history:
        if isinstance(item, dict):
            messages.append(item)
        elif isinstance(item, (list, tuple)) and len(item) == 2:
            messages.append({"role": "user", "content": item[0]})
            messages.append({"role": "assistant", "content": item[1]})
            
    # Add current user message
    messages.append({"role": "user", "content": message})
    
    response = openai.chat.completions.create(model="gpt-4o-mini", messages=messages)
    return response.choices[0].message.content

gr.ChatInterface(chat).launch(server_name="0.0.0.0", inbrowser=True)