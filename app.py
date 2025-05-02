import streamlit as st
from constant import healthcare_assistant_id
from openai import OpenAI
import os
from dotenv import load_dotenv
import time 

# Load environment variables
load_dotenv()

st.title("Voice To Text Assistant")
st.header("AI assistant")

# Configure OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_soap_note():
    try:
        # Read the conversation from file
        with open("conversation.txt", "r", encoding="utf-8") as file:
            conversation = file.read()

        st.info("Generating SOAP note using ChatGPT (gpt-4o)...")

        # Define the system message for dental assistant
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a professional dental assistant. Based on the conversation with the patient, "
                    "generate a detailed and accurate SOAP note. Do not invent information. "
                    "Use today's date for documentation."
                )
            },
            {
                "role": "user",
                "content": (
                    f"{conversation}\n\n=====>\nThis is a dental consultation with a patient. "
                    "Please generate a SOAP (Subjective, Objective, Assessment, Plan) note for this conversation."
                )
            }
        ]

        # Call the ChatGPT API
        response = client.chat.completions.create(
            model="gpt-4o",  # or "gpt-4" if you prefer
            messages=messages,
            temperature=0.4
        )

        # Get the assistant reply
        assistant_response = response.choices[0].message.content

        if assistant_response:
            st.success("SOAP note generated successfully:")
            st.markdown(assistant_response)
        else:
            st.warning("No response generated.")

    except FileNotFoundError:
        st.error("Error: conversation.txt file not found!")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

# Add a button to generate SOAP note
if st.button("Generate SOAP Note"):
    generate_soap_note()

# Add a re-run button
if st.button("Re-run SOAP Note Generation"):
    st.info("Re-running SOAP note generation...")
    generate_soap_note()