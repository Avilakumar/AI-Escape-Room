import os
import streamlit as st
from dotenv import load_dotenv

from game_engine import (
    new_game_state, process_v2_action, build_v2_narration_prompt,
    get_gemini_response, V1_SYSTEM_PROMPT, V1_FALLBACK
)

load_dotenv()

st.set_page_config(
    page_title="AI-Powered Escape Room",
    page_icon="🔐",
    layout="wide"
)

st.title("🔐 AI-Powered Escape Room")
st.caption("An interactive library mystery powered by Python, Streamlit and Gemini.")

with st.sidebar:
    st.header("Game controls")
    version = st.radio(
        "Choose application version",
        ["Version 1 — AI Game Master", "Version 2 — Reliable Game Engine"],
        help="Version 1 lets the LLM manage the story. Version 2 validates game actions in Python."
    )
    st.divider()
    st.markdown("**How to play**")
    st.write("Type natural-language actions such as:")
    st.markdown("- `Examine the desk`")
    st.markdown("- `Look at the painting`")
    st.markdown("- `Use the small key on the drawer`")
    st.markdown("- `Enter code 4826`")
    st.markdown("- `Open the door`")
    if st.button("🔄 Restart game", use_container_width=True):
        st.session_state.v1_messages = []
        st.session_state.v2_state = new_game_state()
        st.session_state.v2_messages = []
        st.rerun()
    st.divider()
    st.caption("Do not enter API keys into the chat. Store them in your .env file.")

# Initialise both versions independently.
if "v1_messages" not in st.session_state:
    st.session_state.v1_messages = []
if "v2_state" not in st.session_state:
    st.session_state.v2_state = new_game_state()
if "v2_messages" not in st.session_state:
    st.session_state.v2_messages = []

if version.startswith("Version 1"):
    st.subheader("Version 1: Interactive AI Escape Room")
    st.info(
        "In this version, the LLM acts as the Game Master and manages the conversation. "
        "As required by the assignment, Version 1 assumes that the player is trying to solve the game normally."
    )

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

    for message in st.session_state.v1_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_text = st.chat_input("What would you like to do?")
    if user_text:
        st.session_state.v1_messages.append({"role": "user", "content": user_text})
        conversation = st.session_state.v1_messages[-16:]
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
        st.session_state.v1_messages.append({"role": "assistant", "content": answer})

else:
    st.subheader("Version 2: Reliable AI Escape Room")
    st.info(
        "Python is the authority for game rules, inventory, puzzle solutions and the door status. "
        "The LLM only narrates outcomes; it cannot decide whether an action succeeds."
    )

    state = st.session_state.v2_state
    left, right = st.columns([2, 1])
    with left:
        st.markdown("**Game conversation**")
        if not st.session_state.v2_messages:
            st.session_state.v2_messages.append({
                "role": "assistant",
                "content": (
                    "You wake up in the same mysterious library. The exit is locked. "
                    "In this improved version, your actions are checked against the game's rules. "
                    "Explore the desk, bookshelf, painting, clock, drawer and door. What will you do?"
                )
            })

        chat_area = st.container(height=390)
        with chat_area:
            for message in st.session_state.v2_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        user_text = st.chat_input("Describe an action or enter a code...", key="v2_chat")
        if user_text:
            st.session_state.v2_messages.append({"role": "user", "content": user_text})
            result = process_v2_action(user_text, st.session_state.v2_state)
            st.session_state.v2_state = result["state"]

            prompt = build_v2_narration_prompt(user_text, result["event"], result["state"])
            narration = get_gemini_response(prompt)
            if not narration:
                narration = result["event"]

            st.session_state.v2_messages.append({"role": "assistant", "content": narration})
            st.rerun()

    with right:
        st.markdown("**Live game state**")
        st.metric("Drawer", "Open" if state["drawer_open"] else "Locked")
        st.metric("Exit door", "Unlocked" if state["door_unlocked"] else "Locked")
        st.metric("Game status", "Escaped" if state["escaped"] else "In progress")
        st.markdown("**Inventory**")
        if state["inventory"]:
            for item in state["inventory"]:
                st.write(f"🎒 {item.replace('_', ' ').title()}")
        else:
            st.caption("No items collected yet.")
        st.markdown("**Solved puzzles**")
        solved = state["solved_puzzles"]
        if solved:
            for puzzle in solved:
                st.write(f"✅ {puzzle.replace('_', ' ').title()}")
        else:
            st.caption("No puzzles solved yet.")
        st.markdown("**Objects discovered**")
        for obj, discovered in state["discovered"].items():
            st.write(f"{'🔎' if discovered else '▫️'} {obj.replace('_', ' ').title()}")

st.divider()
st.caption("Course mini-project | Version 1 and Version 2 are implemented separately for comparison.")
