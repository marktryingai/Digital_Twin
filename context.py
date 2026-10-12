# ==============================================================================
# FILE: context.py
# ==============================================================================
# WHAT THIS CODE DOES EXACTLY:
# This file is responsible for reading your static files (the LinkedIn PDF and 
# the summary text file). 
# It extracts the text from them and combines it into one large set of 
# instructions (the "system prompt"). 
# This system prompt is what tells the AI who it is, how to act, and what 
# information it knows.
# ==============================================================================

# Import the PdfReader class from the pypdf library so we can read PDF files
from pypdf import PdfReader

# 1. LOAD THE LINKEDIN PDF
# Point the reader to your specific PDF file located in the "twin" folder
reader = PdfReader("twin/linkedin.pdf")

# Create an empty string variable where we will store all the text we find in the PDF
linkedin = ""

# Loop through every single page in the PDF document
for page in reader.pages:
    # Extract the text from the current page
    text = page.extract_text()
    # If there is actually text on this page (it's not blank), add it to our 'linkedin' string
    if text:
        linkedin += text

# 2. LOAD THE SUMMARY TEXT FILE
# Open the summary.txt file in "read" mode ("r"). We use utf-8 encoding to prevent errors with special characters.
# Using 'with open' is a best practice because it automatically closes the file when it's done reading.
with open("twin/summary.txt", "r", encoding="utf-8") as f:
    summary = f.read()

# 3. BUILD THE SYSTEM PROMPT
# We use an f-string (indicated by the 'f' before the quotes) so we can easily inject our variables 
# {summary} and {linkedin} directly into the text. This giant block of text is the AI's "brain".
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
"""