from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Function to transcribe voice to text
def transcribe_voice_to_text(file_path):
    with open(file_path, "rb") as audio:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio
        )
    # Save the transcription to a text file
    with open("conversation.txt", "w", encoding="utf-8") as text_file:
        text_file.write(transcript.text)
    return transcript.text

# Transcribe the audio file and save to conversation.txt
transcribe_voice_to_text("./audio/testing-voice.mp3")





