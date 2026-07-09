import streamlit as st
from google import genai
import edge_tts
import asyncio
import time

st.set_page_config(page_title="AI Script + Voiceover Generator", page_icon="🎙️")
st.title("🎙️ AI Script + Voiceover Generator")
st.write("Enter a topic and get a 60-second narration script with voiceover!")

api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

if "script" not in st.session_state:
    st.session_state.script = None
if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None
if "word_count" not in st.session_state:
    st.session_state.word_count = 0

topic = st.text_input("Enter topic:")

if st.button("Generate") and topic:
    prompt = f"""Write a 60-second narration script about: {topic}

Rules:
- Exactly 130-150 words
- First line must be a strong hook that grabs attention
- Conversational, engaging tone
- No stage directions, no speaker labels
- Just the narration text, nothing else"""

    models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite"]

    with st.spinner("Generating script..."):
        for model in models:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )
                st.session_state.script = response.text
                st.session_state.word_count = len(response.text.split())
                break
            except Exception:
                time.sleep(2)
                continue

    if st.session_state.script:
        with st.spinner("Generating voiceover..."):
            async def generate_voice():
                communicate = edge_tts.Communicate(st.session_state.script, "en-US-ChristopherNeural")
                await communicate.save("voiceover.mp3")
            asyncio.run(generate_voice())

            with open("voiceover.mp3", "rb") as f:
                st.session_state.audio_bytes = f.read()
    else:
        st.error("All models are busy. Please try again in a minute.")

if st.session_state.script:
    st.subheader(f"Script ({st.session_state.word_count} words)")
    st.write(st.session_state.script)
    st.download_button("Download Script", st.session_state.script, "script.txt")

if st.session_state.audio_bytes:
    st.audio(st.session_state.audio_bytes, format="audio/mp3")
    st.download_button("Download Voiceover", st.session_state.audio_bytes, "voiceover.mp3")
