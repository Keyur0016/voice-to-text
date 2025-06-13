import streamlit as st
from constant import healthcare_assistant_id, SOAP_NOTE_GENERATION_PROMPT
from openai import OpenAI
import os
from dotenv import load_dotenv
from datetime import datetime
import tempfile
from audio_recorder_streamlit import audio_recorder

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

# Initialize session state
if "recording_complete" not in st.session_state:
    st.session_state.recording_complete = False
if "recorded_audio" not in st.session_state:
    st.session_state.recorded_audio = None

# Audio Recording Section
st.subheader("🎤 Record Audio")
st.write("Click the record button below to start/stop recording:")

# Audio recorder component with custom styling
audio_bytes = audio_recorder(
    text="Click to record",
    recording_color="#e74c3c",
    neutral_color="#2c3e50",
    icon_name="microphone",
    icon_size="2x",
    pause_threshold=2.0,
    sample_rate=41000
)

# Handle recorded audio
if audio_bytes:
    st.session_state.recorded_audio = audio_bytes
    st.session_state.recording_complete = True
    st.success("✅ Recording completed!")
    
    # Play the recorded audio
    st.audio(audio_bytes, format="audio/wav")

# Divider
st.divider()

# File Upload Section (Alternative option)
st.subheader("📁 Or Upload Audio File")
uploaded_file = st.file_uploader("Upload an audio file", type=["mp3", "wav", "m4a"])

# Transcription Section
st.subheader("📝 Transcribe Audio")

# Determine which audio source to use
audio_source = None
source_type = None

if st.session_state.recording_complete and st.session_state.recorded_audio:
    audio_source = st.session_state.recorded_audio
    source_type = "recorded"
    st.info("Using recorded audio for transcription")
elif uploaded_file:
    audio_source = uploaded_file
    source_type = "uploaded"
    st.info("Using uploaded file for transcription")

# Transcribe button
if audio_source and st.button("🔄 Transcribe Audio", type="primary"):
    with st.spinner("Transcribing audio..."):
        try:
            if source_type == "recorded":
                # Save recorded audio to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                    tmp_file.write(audio_source)
                    tmp_file.flush()
                    
                    # Open the temporary file for transcription
                    with open(tmp_file.name, "rb") as audio_file:
                        transcript_text = transcribe_audio(audio_file)
                
                # Clean up temporary file
                os.unlink(tmp_file.name)
                
            else:  # uploaded file
                transcript_text = transcribe_audio(audio_source)
            
            st.session_state["transcript_text"] = transcript_text
            
            # Save transcript to file
            filename = get_unique_filename()
            with open(filename, "w", encoding="utf-8") as file:
                file.write(transcript_text)
            
            st.success(f"✅ Transcript saved as `{filename}`")
            
        except Exception as e:
            st.error(f"Error during transcription: {str(e)}")

# Show transcript if it exists
if "transcript_text" in st.session_state:
    st.divider()
    st.subheader("📄 Transcript")
    
    # Editable transcript
    edited_transcript = st.text_area(
        "Review and edit transcript if needed:",
        st.session_state["transcript_text"],
        height=300,
        help="You can edit the transcript before generating the SOAP note"
    )
    
    # Update session state if transcript was edited
    if edited_transcript != st.session_state["transcript_text"]:
        st.session_state["transcript_text"] = edited_transcript

    # SOAP Note Generation
    st.divider()
    st.subheader("🏥 Generate SOAP Note")
    
    if st.button("📋 Generate SOAP Note", type="primary"):
        with st.spinner("Generating SOAP note..."):
            try:
                soap_note = generate_soap_note(st.session_state["transcript_text"])
                st.session_state["soap_note"] = soap_note
                st.success("✅ SOAP note generated successfully!")
            except Exception as e:
                st.error(f"Error generating SOAP note: {str(e)}")

# Show SOAP note if it exists
if "soap_note" in st.session_state:
    st.divider()
    st.subheader("📋 SOAP Note")
    st.markdown(st.session_state["soap_note"])
    
    # Download button for SOAP note
    soap_filename = f"soap_note_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
    st.download_button(
        label="💾 Download SOAP Note",
        data=st.session_state["soap_note"],
        file_name=soap_filename,
        mime="text/plain"
    )

# Clear session button
st.divider()
if st.button("🗑️ Clear All Data", type="secondary"):
    # Clear all session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()