
import os
import json
import gradio as gr
from dotenv import load_dotenv

import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI

from models import Person
from extraction import create_extraction_chain, try_extract_person_from_text
from validation_utils import validate_with_autocorrect
load_dotenv()


API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY not found. Please set it in your .env file.")
genai.configure(api_key=API_KEY)


MODEL_ID = "gemini-1.5-flash-latest"


try:
    llm = ChatGoogleGenerativeAI(model=MODEL_ID, google_api_key=API_KEY)
    extraction_chain = create_extraction_chain(llm)
    print("✅ LLM and extraction chain initialized successfully.")
except Exception as e:
    print(f"❌ Error initializing LLM: {e}")
    llm = None
    extraction_chain = None


# LOGIC 

def respond(user_msg: str) -> str:
    """
    Main response function that orchestrates the extraction, validation, and fallback chat.
    """
    if not llm or not extraction_chain:
        return "Sorry, the language model is not available. Please check the API key and configuration."

    
    maybe_person = try_extract_person_from_text(user_msg, extraction_chain)

    if maybe_person:
        
        person, info = validate_with_autocorrect(maybe_person.model_dump(), MODEL_ID)

        if person:
            
            msg = "✅ Extracted & validated contact:\n" + json.dumps(person.model_dump(), indent=2)
            if info.get("email_correction"):
                msg += "\n\n(Note: Applied regex fix to email) " + json.dumps(info["email_correction"])
            if info.get("llm_email_correction"):
                msg += "\n\n(Note: Applied LLM fix to email) " + json.dumps(info["llm_email_correction"])
            return msg
        else:
            error_details = info.get("errors") or "Unknown validation error."
            return f"⚠️ Could not validate the extracted contact details:\n\n{error_details}"

    try:
        response = llm.invoke([("human", user_msg)])
        return response.content
    except Exception as e:
        return f"An error occurred during fallback chat: {e}"


# --- GRADIO UI ---

def launch_app():
    """
    Launches the Gradio web interface.
    """
    with gr.Blocks(title="Gemini Contact Extractor", theme=gr.themes.Soft()) as demo:
        gr.Markdown("## 🤖 Gemini Contact Extractor Chatbot")
        gr.Markdown(
            "Enter a message with contact details (name, age, email, phone). "
            "The chatbot will try to extract, validate, and auto-correct the information."
        )

        chatbot = gr.Chatbot(height=450, label="Chat History")
        msg_textbox = gr.Textbox(
            placeholder="e.g., Hi, I'm Raj, 22 yrs old. Email is raj_22 at gamil,com and phone is 09876 543210",
            label="Your Message",
            scale=4
        )
        clear_button = gr.ClearButton(components=[msg_textbox, chatbot], value="Clear Chat")

        def on_submit(user_input, history):
            bot_reply = respond(user_input)
            history.append((user_input, bot_reply))
            return "", history

        msg_textbox.submit(on_submit, [msg_textbox, chatbot], [msg_textbox, chatbot])

    print("Launching Gradio App...")
    demo.launch()

if __name__ == "__main__":
    launch_app()