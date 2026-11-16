
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Access the original game_engine.py
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from game_engine import (
    new_game_state,
    process_v2_action,
    build_v2_narration_prompt,
    get_gemini_response,
)

load_dotenv()

st.set_page_config(
    page_title="AI Escape Room - Version 2",
    page_icon="🔐",
    layout="wide"
)

st.title("🔐 AI-Powered Escape Room")
st.caption("An interactive library mystery powered by Python, Streamlit and Gemini.")

st.subheader("Version 2 – Rule-Based Stateful Game Engine")

st.info(
    "Python validates every action and controls the game state. "
    "Gemini is responsible for generating narrative responses."
)

# Initialise game state
if "v2_state" not in st.session_state:
    st.session_state.v2_state = new_game_state()

if "v2_messages" not in st.session_state:
    st.session_state.v2_messages = []

with st.sidebar:
    st.header("Game controls")

    st.markdown("**How to play – Complete all steps**")
    st.markdown("""
    1. Examine the desk.
    2. Examine the painting.
    3. Examine the bookshelf.
    4. Inspect the locked drawer.
    5. Use the small brass key and enter code `4826`.
    6. Read the note inside the drawer.
    7. Enter exit code `7319`.
    8. Open the exit door.
    
    **Goal:** Discover all clues and escape the library!
    """)

    if st.button("🔄 Restart game", use_container_width=True):
        st.session_state.v2_state = new_game_state()
        st.session_state.v2_messages = []
        st.rerun()

    st.divider()
    st.caption("Python controls the game rules. Gemini generates narration.")

state = st.session_state.v2_state

# Initial game message
if not st.session_state.v2_messages:
    st.session_state.v2_messages.append({
        "role": "assistant",
        "content": (
            "You wake up inside a mysterious library. "
            "The exit door is locked. Explore the desk, bookshelf, "
            "painting and grandfather clock to discover the clues. "
            "What would you like to do?"
        )
    })

left, right = st.columns([2, 1])

with left:
    st.markdown("### Game conversation")

    for message in st.session_state.v2_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_text = st.chat_input("Describe an action or enter a code...")

    if user_text:
        st.session_state.v2_messages.append({
            "role": "user",
            "content": user_text
        })

        # Validate action using the original Python game engine
        result = process_v2_action(
            user_text,
            st.session_state.v2_state
        )

        st.session_state.v2_state = result["state"]

        # Generate narration using the original Version 2 prompt builder
        prompt = build_v2_narration_prompt(
            user_text,
            result["event"],
            result["state"]
        )

        narration = get_gemini_response(prompt)

        if not narration:
            narration = result["event"]

        st.session_state.v2_messages.append({
            "role": "assistant",
            "content": narration
        })

        st.rerun()

with right:
    st.markdown("### Live game state")

    state = st.session_state.v2_state

    st.metric(
        "Drawer",
        "Open" if state["drawer_open"] else "Locked"
    )

    st.metric(
        "Exit door",
        "Unlocked" if state["door_unlocked"] else "Locked"
    )

    st.metric(
        "Game status",
        "Escaped" if state["escaped"] else "In progress"
    )

    st.markdown("**Inventory**")

    if state["inventory"]:
        for item in state["inventory"]:
            st.write(f"🎒 {item.replace('_', ' ').title()}")
    else:
        st.caption("No items collected yet.")

    st.markdown("**Solved puzzles**")

    if state["solved_puzzles"]:
        for puzzle in state["solved_puzzles"]:
            st.write(f"✅ {puzzle.replace('_', ' ').title()}")
    else:
        st.caption("No puzzles solved yet.")

    st.markdown("**Discovered objects**")

    for obj, discovered in state["discovered"].items():
        st.write(
            f"{'🔎' if discovered else '▫️'} "
            f"{obj.replace('_', ' ').title()}"
        )

    if state["escaped"]:
        st.success("🎉 Congratulations! You escaped the library!")

st.divider()
st.caption("Version 2 – Rule-Based Stateful Game Engine")
