import streamlit as st
from google import genai
import edge_tts
import asyncio
import time

st.set_page_config(page_title="AI Script + Voiceover Generator", page_icon="🎙️", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    .stApp {
        background: #111827;
        font-family: 'Inter', sans-serif;
    }
    
    .hero-card {
        background: linear-gradient(145deg, #1e3a5f, #0f2027);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 20px;
        padding: 2.5rem 2rem;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 0 40px rgba(56, 189, 248, 0.08);
    }
    
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-top: 0.5rem;
    }
    
    .feature-row {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin-top: 1.5rem;
    }
    
    .feature-chip {
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.25);
        color: #38bdf8;
        padding: 6px 16px;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .script-box {
        background: linear-gradient(145deg, #1a1f35, #151928);
        border: 1px solid rgba(129, 140, 248, 0.2);
        border-radius: 16px;
        padding: 2rem;
        margin: 1.5rem 0;
        line-height: 1.9;
        color: #e2e8f0;
        font-size: 1.05rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    
    .word-badge {
        background: linear-gradient(135deg, #22c55e, #16a34a);
        color: #fff;
        padding: 6px 18px;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(34, 197, 94, 0.3);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6, #a855f7);
        color: #ffffff;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-size: 1.15rem;
        font-weight: 700;
        width: 100%;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #818cf8, #a78bfa, #c084fc);
        box-shadow: 0 6px 25px rgba(99, 102, 241, 0.5);
        transform: translateY(-1px);
    }
    
    .stDownloadButton > button {
        background: rgba(99, 102, 241, 0.15);
        color: #a5b4fc;
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        background: rgba(99, 102, 241, 0.25);
        border-color: rgba(99, 102, 241, 0.5);
    }
    
    .stTextInput > div > div > input {
        background: #1e293b;
        color: #f1f5f9;
        border: 1px solid #334155;
        border-radius: 12px;
        font-size: 1.1rem;
        padding: 0.75rem 1rem;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #64748b;
    }
    
    .audio-section {
        background: linear-gradient(145deg, #1a1f35, #151928);
        border: 1px solid rgba(56, 189, 248, 0.15);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .footer {
        text-align: center;
        color: #475569;
        margin-top: 3rem;
        font-size: 0.85rem;
    }
    
    .stSpinner > div {
        color: #818cf8;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-card">
    <div class="main-title">🎙️ AI Script + Voiceover</div>
    <p class="subtitle">Type a topic. Get a broadcast-ready script + professional voiceover in seconds.</p>
    <div class="feature-row">
        <span class="feature-chip">⚡ 60-Sec Scripts</span>
        <span class="feature-chip">🎧 Pro Voice</span>
        <span class="feature-chip">📥 Instant Download</span>
    </div>
</div>
""", unsafe_allow_html=True)

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

st.markdown('<p class="footer">Powered by Gemini AI + Edge-TTS</p>', unsafe_allow_html=True)
