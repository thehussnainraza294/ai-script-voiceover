import streamlit as st
from google import genai
import edge_tts
import asyncio
import time

st.set_page_config(page_title="AI Script + Voiceover Generator", page_icon="🎙️", layout="centered")

st.markdown("""
<style>
    .stApp {
        background: #0a0a0a;
        color: #f0f0f0;
    }
    .main-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 0;
    }
    .subtitle {
        text-align: center;
        color: #888;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .script-box {
        background: #161616;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        line-height: 1.8;
        color: #e0e0e0;
    }
    .word-badge {
        background: #22c55e;
        color: #000;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 1rem;
    }
    .stButton > button {
        background: #ffffff;
        color: #000000;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        width: 100%;
    }
    .stButton > button:hover {
        background: #e0e0e0;
        color: #000000;
    }
    .stDownloadButton > button {
        background: #1a1a1a;
        color: #fff;
        border: 1px solid #333;
        border-radius: 8px;
    }
    .stTextInput > div > div > input {
        background: #161616;
        color: white;
        border: 1px solid #333;
        border-radius: 8px;
        font-size: 1.1rem;
    }
    .footer {
        text-align: center;
        color: #444;
        margin-top: 3rem;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🎙️ AI Script + Voiceover Generator</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Enter a topic and get a 60-second narration script with professional voiceover</p>', unsafe_allow_html=True)

api_key = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=api_key)

if "script" not in st.session_state:
    st.session_state.script = None
if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None
if "word_count" not in st.session_state:
    st.session_state.word_count = 0

topic = st.text_input("", placeholder="e.g. Why sleep is the secret weapon of successful people")

if st.button("🚀 Generate Script + Voiceover") and topic:
    prompt = f"""Write a 60-second narration script about: {topic}

Rules:
- Exactly 130-150 words
- First line must be a strong hook that grabs attention
- Conversational, engaging tone
- No stage directions, no speaker labels
- Just the narration text, nothing else"""

    models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite"]

    with st.spinner("✨ Crafting your script..."):
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
        with st.spinner("🎧 Generating voiceover..."):
            async def generate_voice():
                communicate = edge_tts.Communicate(st.session_state.script, "en-US-ChristopherNeural")
                await communicate.save("voiceover.mp3")
            asyncio.run(generate_voice())

            with open("voiceover.mp3", "rb") as f:
                st.session_state.audio_bytes = f.read()
    else:
        st.error("All models are busy. Please try again in a minute.")

if st.session_state.script:
    st.markdown(f'<span class="word-badge">📝 {st.session_state.word_count} words</span>', unsafe_allow_html=True)
    st.markdown(f'<div class="script-box">{st.session_state.script}</div>', unsafe_allow_html=True)
    st.download_button("📄 Download Script", st.session_state.script, "script.txt")

if st.session_state.audio_bytes:
    st.audio(st.session_state.audio_bytes, format="audio/mp3")
    st.download_button("🎵 Download Voiceover", st.session_state.audio_bytes, "voiceover.mp3")

st.markdown('<p class="footer">Built with Gemini AI + Edge-TTS</p>', unsafe_allow_html=True)
