from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
from IPython.display import Markdown, display
import gradio as gr
import json

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


    messages = [
    {"role": "system", "content": "You are a snarky, witty assistant"},
    {"role": "user", "content": "Hi, my name is Mark"},
    {"role": "assistant", "content": "Well hi there, Ed. It's nice to meet you."},
    {"role": "user", "content": "What's my name?"}
]

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


messages = [
    {"role": "system", "content": "You are a snarky, witty assistant"},
    {"role": "user", "content": "Hi, my name is Mark"}
]

response = openai.chat.completions.create(model="gpt-5.4-nano", messages=messages)
print(response.choices[0].message.content)

def chat(message, history):
    #return "You said: " + message
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]
    response = openai.chat.completions.create(model="gpt-5.4-mini", messages=messages)
    return response.choices[0].message.content

chat("Please summarize who you are", [])

gr.ChatInterface(chat).launch(inbrowser=True)

