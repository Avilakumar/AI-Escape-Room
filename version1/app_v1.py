
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Access the original game_engine.py in the project root
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from game_engine import (
    get_gemini_response,
    V1_SYSTEM_PROMPT,
    V1_FALLBACK
)

load_dotenv()

st.set_page_config(
    page_title="AI-Powered Escape Room - Version 1",
    page_icon="🔐",
    layout="wide"
)

st.title("🔐 AI-Powered Escape Room")
st.caption("An interactive library mystery powered by Python, Streamlit and Gemini.")

st.subheader("Version 1: Interactive AI Escape Room")

st.info(
    "In this version, the LLM acts as the Game Master and manages the conversation. "
    "As required by the assignment, Version 1 assumes that the player is trying to solve the game normally."
)


with st.sidebar:
    st.header("Game controls")

    st.markdown("**How to play – Complete all steps**")
    st.markdown("""
    1. Examine the desk.
    2. Search under the blotter.
    3. Look at the painting
    4. Examine the bookshelf.
    5. Inspect the locked drawer.
    6. Use the small key on the drawer.
    7. Enter code 4826
    8. Read the note.
    9. Enter exit code `7319`.
    10. Open the exit door.

    **Goal:** Discover all clues and escape the library!
    """)

    if st.button("🔄 Restart game", use_container_width=True):
        st.session_state.v1_messages = []
        st.rerun()

    st.divider()
    st.caption("Do not enter API keys into the chat. Store them in your .env file.")


# Initialise Version 1 conversation
if "v1_messages" not in st.session_state:
    st.session_state.v1_messages = []

if not st.session_state.v1_messages:
    st.session_state.v1_messages.append({
        "role": "assistant",
        "content": (
            "You wake up on the cold wooden floor of an old library. Rain taps against "
            "the windows. A heavy exit door is locked. Around you are a desk, a bookshelf, "
            "a painting, a locked drawer, a grandfather clock and the exit door. "
            "You need to investigate, discover clues and escape. What would you like to do?"
        )
    })

# Display conversation history
for message in st.session_state.v1_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Player input
user_text = st.chat_input("What would you like to do?")

if user_text:
    st.session_state.v1_messages.append({
        "role": "user",
        "content": user_text
    })

    conversation = st.session_state.v1_messages[-16:]

    # Original Version 1 system prompt from game_engine.py
    prompt = V1_SYSTEM_PROMPT + "\n\nConversation so far:\n" + "\n".join(
        f'{m["role"].upper()}: {m["content"]}' for m in conversation
    )

    with st.chat_message("user"):
        st.markdown(user_text)

    with st.chat_message("assistant"):
        with st.spinner("The Game Master is thinking..."):
            answer = get_gemini_response(prompt)

            if not answer:
                answer = V1_FALLBACK

            st.markdown(answer)

    st.session_state.v1_messages.append({
        "role": "assistant",
        "content": answer
    })
