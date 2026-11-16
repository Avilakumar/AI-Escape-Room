
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Project root and original game engine
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from game_engine import (
    new_game_state,
    process_v2_action,
    build_v2_narration_prompt,
    get_gemini_response,
    V1_SYSTEM_PROMPT,
    V1_FALLBACK,
)

load_dotenv()

# --------------------------- PAGE CONFIGURATION ---------------------------

st.set_page_config(
    page_title="AI-Powered Escape Room",
    page_icon="🔐",
    layout="wide"
)

st.title("🔐 AI-Powered Escape Room")
st.caption(
    "An interactive library mystery powered by Python, Streamlit and Gemini."
)

# --------------------------- SESSION INITIALIZATION -----------------------

if "v1_messages" not in st.session_state:
    st.session_state.v1_messages = []

if "v2_state" not in st.session_state:
    st.session_state.v2_state = new_game_state()

if "v2_messages" not in st.session_state:
    st.session_state.v2_messages = []


# --------------------------- SIDEBAR CONTROLS -----------------------------

with st.sidebar:
    st.header("🎮 Game controls")

    version = st.radio(
        "Choose application version",
        [
            "Version 1 — AI Game Master",
            "Version 2 — Rule-Based Game Engine"
        ],
        help=(
            "Version 1 uses Gemini as the Game Master. "
            "Version 2 uses Python to validate game actions."
        )
    )

    st.divider()

    if version.startswith("Version 1"):

        st.markdown("**How to play – Version 1**")
        st.write("Interact naturally with the AI Game Master:")

        st.markdown("""
        1. Examine the desk.
        2. Search under the blotter.
        3. Look at the painting.
        4. Examine the bookshelf.
        5. Inspect the locked drawer.
        6. Use the small brass key.
        7. Enter code `4826`.
        8. Read the note.
        9. Enter exit code `7319`.
        10. Open the exit door.
        """)

        st.caption(
            "Gemini manages the story and interprets player actions."
        )

    else:

        st.markdown("**How to play – Version 2**")

        st.markdown("""
        1. Examine the desk.
        2. Examine the painting.
        3. Examine the bookshelf.
        4. Inspect the locked drawer.
        5. Use the key and enter code `4826`.
        6. Read the note.
        7. Enter exit code `7319`.
        8. Open the exit door.
        """)

        st.caption(
            "Python validates actions and controls the game state."
        )

    st.divider()

    if st.button("🔄 Restart game", use_container_width=True):
        st.session_state.v1_messages = []
        st.session_state.v2_state = new_game_state()
        st.session_state.v2_messages = []
        st.rerun()

    st.caption(
        "Do not enter API keys into the chat. Store them in your .env file."
    )


# =============================== VERSION 1 ================================

if version.startswith("Version 1"):

    st.subheader("Version 1: Interactive AI Escape Room")

    st.info(
        "In this version, Gemini acts as the Game Master. "
        "Players interact through natural-language messages, "
        "and the LLM manages the conversation and story progression."
    )

    # Initial game introduction
    if not st.session_state.v1_messages:

        st.session_state.v1_messages.append({
            "role": "assistant",
            "content": (
                "You wake up on the cold wooden floor of an old library. "
                "Rain taps against the windows. A heavy exit door is locked. "
                "Around you are a desk, a bookshelf, a painting, a locked drawer, "
                "a grandfather clock and the exit door. "
                "You need to investigate, discover clues and escape. "
                "What would you like to do?"
            )
        })

    # Display Version 1 conversation
    for message in st.session_state.v1_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_text = st.chat_input(
        "What would you like to do?",
        key="v1_chat_input"
    )

    if user_text:

        st.session_state.v1_messages.append({
            "role": "user",
            "content": user_text
        })

        conversation = st.session_state.v1_messages[-16:]

        # Original Version 1 system prompt
        prompt = (
            V1_SYSTEM_PROMPT
            + "\n\nConversation so far:\n"
            + "\n".join(
                f'{m["role"].upper()}: {m["content"]}'
                for m in conversation
            )
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


# =============================== VERSION 2 ================================

else:

    st.subheader("Version 2: Rule-Based Stateful Game Engine")

    st.info(
        "Python validates every action and controls the game state, "
        "including inventory, puzzle solutions and escape conditions. "
        "Gemini generates narration only after Python validates an action."
    )

    # Initial Version 2 state
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

        st.markdown("### 💬 Game conversation")

        for message in st.session_state.v2_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        user_text = st.chat_input(
            "Describe an action or enter a code...",
            key="v2_chat_input"
        )

        if user_text:

            st.session_state.v2_messages.append({
                "role": "user",
                "content": user_text
            })

            # Python validates the player's action
            result = process_v2_action(
                user_text,
                st.session_state.v2_state
            )

            st.session_state.v2_state = result["state"]

            # Original Version 2 narration prompt
            prompt = build_v2_narration_prompt(
                user_text,
                result["event"],
                result["state"]
            )

            narration = get_gemini_response(prompt)

            # Python event is the fallback
            if not narration:
                narration = result["event"]

            st.session_state.v2_messages.append({
                "role": "assistant",
                "content": narration
            })

            st.rerun()

    # ----------------------- VERSION 2 GAME STATE -------------------------

    with right:

        st.markdown("### 📊 Live game state")

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

        st.divider()

        st.markdown("**🎒 Inventory**")

        if state["inventory"]:

            for item in state["inventory"]:
                st.write(
                    f"🎒 {item.replace('_', ' ').title()}"
                )

        else:
            st.caption("No items collected yet.")

        st.divider()

        st.markdown("**🧩 Solved puzzles**")

        if state["solved_puzzles"]:

            for puzzle in state["solved_puzzles"]:
                st.write(
                    f"✅ {puzzle.replace('_', ' ').title()}"
                )

        else:
            st.caption("No puzzles solved yet.")

        st.divider()

        st.markdown("**🔎 Discovered objects**")

        for obj, discovered in state["discovered"].items():

            st.write(
                f"{'🔎' if discovered else '▫️'} "
                f"{obj.replace('_', ' ').title()}"
            )

        if state["escaped"]:
            st.success(
                "🎉 Congratulations! You escaped the library!"
            )


# ------------------------------- FOOTER -----------------------------------

st.divider()

st.caption(
    "AI-Powered Escape Room | Master of Science – Data Science | "
    "Version 1 and Version 2"
)
