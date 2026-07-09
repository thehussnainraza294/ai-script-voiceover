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
    script = None

    with st.spinner("Generating script..."):
        for model in models:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )
                script = response.text
                break
            except Exception:
                time.sleep(2)
                continue

    if script:
        word_count = len(script.split())
        st.subheader(f"Script ({word_count} words)")
        st.write(script)
        st.download_button("Download Script", script, "script.txt")

        with st.spinner("Generating voiceover..."):
            async def generate_voice():
                communicate = edge_tts.Communicate(script, "en-US-ChristopherNeural")
                await communicate.save("voiceover.mp3")
            asyncio.run(generate_voice())

        with open("voiceover.mp3", "rb") as f:
            audio_bytes = f.read()
        st.audio(audio_bytes, format="audio/mp3")
        st.download_button("Download Voiceover", audio_bytes, "voiceover.mp3")
    else:
        st.error("All models are busy. Please try again in a minute.")
