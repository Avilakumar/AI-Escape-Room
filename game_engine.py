import os
import re
from typing import Dict, Any

try:
    from google import genai
except ImportError:
    genai = None


# --------------------------- GEMINI CONFIGURATION ---------------------------

def get_gemini_response(prompt: str) -> str:
    """Generate a response with Gemini. Return an empty string if unavailable."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    if not api_key or genai is None:
        return ""

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        return (response.text or "").strip()
    except Exception:
        return ""


# ------------------------------- VERSION 1 ---------------------------------

V1_SYSTEM_PROMPT = """
You are the Game Master for an interactive AI escape-room game set in a mysterious library.

The player wakes up trapped inside. The room contains six interactive objects:
1. Desk
2. Bookshelf
3. Painting
4. Locked drawer
5. Grandfather clock
6. Exit door

GAME STORY AND FIXED SOLUTION:
- The desk contains a small brass key hidden under a blotter.
- The painting shows the correct order of four symbols: Star, Moon, Tree, Sun.
- The bookshelf contains four marked books:
  Star = 4, Moon = 8, Tree = 2, Sun = 6.
- The drawer code is 4826.
- The small brass key and code 4826 are needed to open the drawer.
- Inside the drawer is a note with the final exit code 7319.
- Entering 7319 at the exit door allows the player to escape.


IMPORTANT GAMEPLAY RULES:
1. When the player enters the correct drawer code 4826 with the small brass key, open the drawer.
2. Do NOT automatically pick up, read, or reveal the note.
3. After the drawer opens, describe the folded note without revealing its contents.
4. Only reveal the final exit code 7319 when the player explicitly asks to read, inspect, or unfold the note.
5. Do not unlock the exit door until the player enters 7319.
6. The player must explicitly ask to open the exit door after entering the correct code.
7. Never skip a puzzle step or perform an action on behalf of the player.
"""

V1_FALLBACK = (
    "The Game Master is currently unavailable because the Gemini API key is missing, "
    "the model request failed, or the API quota was reached. You can still test Version 2, "
    "where Python validates the game rules."
)


# ------------------------------- VERSION 2 ---------------------------------

OBJECT_NAMES = ["desk", "bookshelf", "painting", "clock", "drawer", "door"]


def new_game_state() -> Dict[str, Any]:
    """Create a fresh, structured state for Version 2."""
    return {
        "inventory": [],
        "discovered": {name: False for name in OBJECT_NAMES},
        "desk_examined": False,
        "painting_examined": False,
        "bookshelf_examined": False,
        "clock_examined": False,
        "drawer_open": False,
        "final_note_read": False,
        "door_unlocked": False,
        "escaped": False,
        "solved_puzzles": [],
        "history": []
    }


def _contains_any(text: str, terms) -> bool:
    return any(term in text for term in terms)


def _add_item(state, item):
    if item not in state["inventory"]:
        state["inventory"].append(item)


def process_v2_action(user_text: str, state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate a natural-language action using Python.

    Python controls every state transition.
    The player must read the final note before entering 7319.
    The player must separately open the unlocked door to escape.
    """
    text = user_text.lower().strip()
    event = ""

    def finish(message: str):
        state["history"].append({
            "action": user_text,
            "result": message
        })
        return {"state": state, "event": message}

    if state["escaped"]:
        return finish("You have already escaped. Restart the game to play again.")

    # Open the exit door only after it has been unlocked.
    if (
        _contains_any(text, ["open", "push", "pull"])
        and _contains_any(text, ["door", "exit"])
    ):
        state["discovered"]["door"] = True

        if state["door_unlocked"]:
            state["escaped"] = True
            return finish(
                "SUCCESS: You open the unlocked exit door and escape the library!"
            )

        return finish(
            "The exit door is still locked. You must first retrieve the final "
            "code note from the drawer and enter 7319 at the exit keypad."
        )

    # Validate four-digit code attempts.
    code_match = re.search(r"\b(\d{4})\b", text)

    if code_match:
        entered_code = code_match.group(1)

        door_attempt = (
            _contains_any(text, ["door", "exit", "keypad"])
            or entered_code == "7319"
        )

        if door_attempt:
            state["discovered"]["door"] = True

            if entered_code != "7319":
                event = (
                    "INCORRECT: That is not the correct exit code. "
                    "The door remains locked."
                )

            elif not state.get("final_note_read", False):
                event = (
                    "ACCESS DENIED: You have not read the final code note yet. "
                    "Open the drawer and read the note before entering the exit code."
                )

            else:
                state["door_unlocked"] = True

                if "final_door_code" not in state["solved_puzzles"]:
                    state["solved_puzzles"].append("final_door_code")

                event = (
                    "SUCCESS: The code 7319 is correct. The exit door unlocks. "
                    "You must now open the door to escape."
                )

        else:
            state["discovered"]["drawer"] = True

            if entered_code != "4826":
                event = (
                    "INCORRECT: The drawer combination is wrong. "
                    "It remains locked."
                )

            elif "small_brass_key" not in state["inventory"]:
                event = (
                    "ACCESS DENIED: The combination is correct, "
                    "but you must collect the small brass key first."
                )

            elif not (
                state["painting_examined"]
                and state["bookshelf_examined"]
            ):
                event = (
                    "ACCESS DENIED: You must examine both the painting and "
                    "the bookshelf to solve the symbol puzzle before opening "
                    "the drawer."
                )

            else:
                state["drawer_open"] = True
                _add_item(state, "final_code_note")

                if "bookshelf_symbol_code" not in state["solved_puzzles"]:
                    state["solved_puzzles"].append("bookshelf_symbol_code")

                if "drawer_puzzle" not in state["solved_puzzles"]:
                    state["solved_puzzles"].append("drawer_puzzle")

                event = (
                    "SUCCESS: The key and code 4826 open the drawer. "
                    "Inside, you discover a folded handwritten note."
                )

        return finish(event)

    # Read the note only after opening the drawer.
    if (
        _contains_any(text, ["read", "inspect", "examine", "look at"])
        and _contains_any(text, ["note", "paper"])
    ):
        if (
            not state["drawer_open"]
            or "final_code_note" not in state["inventory"]
        ):
            event = (
                "You have not found the note yet. "
                "First unlock and open the drawer."
            )

        elif state.get("final_note_read", False):
            event = (
                "You have already read the note. "
                "The final exit code is 7319."
            )

        else:
            state["final_note_read"] = True
            event = (
                "You unfold the handwritten note. Written clearly across "
                "the paper is the final exit code: 7319."
            )

        return finish(event)

    # Use the key on the drawer.
    if (
        _contains_any(text, ["use", "try", "insert"])
        and _contains_any(text, ["key"])
        and _contains_any(text, ["drawer"])
    ):
        state["discovered"]["drawer"] = True

        if "small_brass_key" not in state["inventory"]:
            event = (
                "You do not have the small brass key in your inventory. "
                "Examine the desk first."
            )

        elif not state["drawer_open"]:
            event = (
                "The key fits, but the drawer also needs its four-digit code. "
                "Use the painting and bookshelf clues to work it out."
            )

        else:
            event = "The drawer is already open. You have the final code note."

        return finish(event)

    # Examine desk and collect the small brass key.
    if _contains_any(text, ["desk", "blotter"]):
        state["discovered"]["desk"] = True
        state["desk_examined"] = True
        _add_item(state, "small_brass_key")

        event = (
            "You examine the desk and lift the leather blotter. "
            "A small brass key is hidden underneath. "
            "You collect the small brass key."
        )

        return finish(event)

    # Examine painting and reveal symbol order.
    if _contains_any(text, ["painting", "picture", "canvas"]):
        state["discovered"]["painting"] = True
        state["painting_examined"] = True

        event = (
            "The painting shows four symbols in this exact order: "
            "Star, Moon, Tree, Sun. Remember this sequence; it is connected "
            "to the marked books on the bookshelf."
        )

        if (
            state["bookshelf_examined"]
            and "bookshelf_symbol_code" not in state["solved_puzzles"]
        ):
            state["solved_puzzles"].append("bookshelf_symbol_code")

        return finish(event)

    # Examine bookshelf and reveal symbol numbers.
    if _contains_any(text, ["bookshelf", "bookcase", "books", "book"]):
        state["discovered"]["bookshelf"] = True
        state["bookshelf_examined"] = True

        event = (
            "You find four marked books. Their symbols and numbers are: "
            "Star = 4, Moon = 8, Tree = 2, Sun = 6. Use the order shown "
            "in the painting to form the four-digit drawer code."
        )

        if (
            state["painting_examined"]
            and "bookshelf_symbol_code" not in state["solved_puzzles"]
        ):
            state["solved_puzzles"].append("bookshelf_symbol_code")

        return finish(event)

    # Examine grandfather clock.
    if _contains_any(text, ["clock", "grandfather"]):
        state["discovered"]["clock"] = True
        state["clock_examined"] = True

        event = (
            "The grandfather clock has stopped at 7:19. The hands seem "
            "unusually clean, as if someone wanted you to notice the time. "
            "Keep this in mind when you discover the final clue."
        )

        return finish(event)

    # Inspect the drawer without entering a code.
    if _contains_any(text, ["drawer"]):
        state["discovered"]["drawer"] = True

        if state["drawer_open"]:
            if state.get("final_note_read", False):
                event = (
                    "The drawer is open. You have already read the note "
                    "containing the final exit code: 7319."
                )
            else:
                event = (
                    "The drawer is open. A folded handwritten note is inside. "
                    "You should read it."
                )

        elif "small_brass_key" not in state["inventory"]:
            event = (
                "The drawer is locked. It has a keyhole and a four-digit "
                "combination lock. You need a small brass key and the correct code."
            )

        else:
            event = (
                "You have the small brass key, but the four-digit combination "
                "lock is still engaged. Examine the painting and bookshelf "
                "for the code."
            )

        return finish(event)

    # Inspect the exit door without entering a code.
    if _contains_any(text, ["door", "exit", "keypad"]):
        state["discovered"]["door"] = True

        if state["door_unlocked"]:
            event = "The exit door is unlocked. Open the door to escape."

        elif not state.get("final_note_read", False):
            event = (
                "The exit door has a keypad. You must open the drawer and "
                "read the final code note before entering the code."
            )

        else:
            event = (
                "You have read the final code note. "
                "Enter 7319 at the exit keypad to unlock the door."
            )

        return finish(event)

    # Inventory and hints.
    if _contains_any(
        text,
        ["inventory", "items", "what do i have", "what have i collected"]
    ):
        items = (
            ", ".join(state["inventory"])
            if state["inventory"]
            else "nothing"
        )
        event = f"Your inventory contains: {items}."

    elif _contains_any(text, ["help", "hint", "stuck"]):
        event = (
            "Hint: Examine every object. The desk may hide a useful item. "
            "The painting and bookshelf are connected. The drawer contains "
            "the clue needed to escape."
        )

    else:
        event = (
            "I cannot identify that as a valid action in this room. Try "
            "examining the desk, bookshelf, painting or clock, inspecting "
            "the drawer, or investigating the exit door."
        )

    return finish(event)


# --------------------------- VERSION 2 NARRATION ----------------------------

def build_v2_narration_prompt(
    player_action: str,
    validated_event: str,
    state: Dict[str, Any]
) -> str:
    """Ask Gemini to narrate a Python-validated result without changing rules."""

    return f"""
You are the atmospheric narrator for a library escape-room game.

The player's action was: {player_action}

Python game engine has already validated the action and produced this result:
{validated_event}

Current authoritative game state:
- Inventory: {state['inventory']}
- Drawer open: {state['drawer_open']}
- Final note read: {state.get('final_note_read', False)}
- Exit unlocked: {state['door_unlocked']}
- Escaped: {state['escaped']}
- Solved puzzles: {state['solved_puzzles']}

Write 1-3 engaging sentences describing ONLY the validated result.

Important:
- Do not change, override or reinterpret the Python result.
- Do not claim an item was collected unless it appears in the inventory.
- Do not claim a puzzle or door was solved unless the state says so.
- Do not say the player escaped unless the Python state has Escaped = True.
- Do not reveal secret codes unless the validated event explicitly reveals them.
- If the event starts with SUCCESS, clearly communicate that success.
"""