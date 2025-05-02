import streamlit as st
from constant import healthcare_assistant_id, SOAP_NOTE_GENERATION_PROMPT
from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

st.title("Voice To Text Assistant")
st.header("AI Assistant")

# Configure OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_unique_filename():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"conversation_{timestamp}.txt"

def transcribe_audio(audio_file):
    st.info("Transcribing audio using Whisper...")
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
    return transcription.text

def generate_soap_note(conversation):
    st.info("Generating SOAP note using ChatGPT...")

    messages = [
        {
            "role": "system",
            "content": SOAP_NOTE_GENERATION_PROMPT
        },
        {
            "role": "user",
            "content": (
                f"{conversation}\n\n=====>\nThis is a dental consultation with a patient. "
                "Please generate a SOAP (Subjective, Objective, Assessment, Plan) note for this conversation."
            )
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4.1-2025-04-14",
        messages=messages,
        temperature=0.4
    )

    return response.choices[0].message.content

# Upload audio
audio_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "m4a"])

if audio_file and st.button("Transcribe Audio"):
    with st.spinner("Transcribing..."):
        transcript_text = transcribe_audio(audio_file)
        st.session_state["transcript_text"] = transcript_text

    filename = get_unique_filename()
    with open(filename, "w", encoding="utf-8") as file:
        file.write(st.session_state["transcript_text"])
    
    st.success(f"Transcript saved as `{filename}`.")

# Show transcript if it exists
if "transcript_text" in st.session_state:
    st.text_area("Transcript", st.session_state["transcript_text"], height=300)

    if st.button("Generate SOAP Note"):
        with st.spinner("Generating SOAP note..."):
            soap_note = generate_soap_note(st.session_state["transcript_text"])
            st.markdown(soap_note)
