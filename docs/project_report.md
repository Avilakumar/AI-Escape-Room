# AI-Powered Escape Room
## Project Report

### 1. Introduction

The AI-Powered Escape Room is an interactive game developed using Python, Streamlit and Google Gemini. The player explores a mysterious library, examines objects, solves puzzles and discovers clues to escape.

The project implements two versions to demonstrate the difference between an LLM-based game system and a rule-based stateful game engine.

### 2. Project Objectives

- Develop an interactive escape room using natural-language input.
- Use an LLM as a Game Master to generate responses and narrate the story.
- Implement multiple objects, clues and puzzles.
- Maintain conversation history and game progress.
- Develop a rule-based engine that validates actions and maintains game state.
- Test correct actions, incorrect actions and invalid sequences.

### 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Interactive user interface |
| Google Gemini API | AI Game Master and narration |
| Dictionaries and JSON-style state | Game-state management |
| Unittest | Automated testing |
| GitHub | Version control and project hosting |

### 4. Game Scenario

The game takes place in a mysterious library containing a desk, bookshelf, painting, locked drawer, grandfather clock and exit door.

The player must discover a brass key, examine the painting and bookshelf, solve the drawer combination and obtain the final exit code.

The puzzle sequence is:
1. Find the brass key hidden in the desk.
2. Discover the symbol order from the painting.
3. Use the bookshelf numbers to calculate the drawer code (4826).
4. Open the drawer and discover the final code (7319).
5. Unlock and open the exit door.

### 5. Version 1 – LLM-Based Game Master

Version 1 uses Google Gemini as the Game Master. The player interacts with the game using natural language.

The application maintains conversation history and sends the player's messages to Gemini along with the game instructions. Gemini interprets actions, provides clues and generates narrative responses.

**Main features:**
- Natural-language interaction.
- AI-generated responses and hints.
- Conversation memory.
- Interactive objects and puzzles.
- Restart functionality.

### 6. Version 2 – Rule-Based Stateful Game Engine

Version 2 introduces a Python-based game engine to manage game rules and state.

The `game_engine.py` module recognises player actions, validates them against predefined conditions and updates the game state.

The game tracks inventory, examined objects, puzzle progress, drawer status, door status and escape completion.

For example, the drawer code 4826 is accepted only when the player has the brass key and has examined both the painting and bookshelf. The final code 7319 unlocks the exit, but the player must separately open the door to escape.

Gemini is used for narration, while Python controls the actual game rules and outcomes.

### 7. Testing and Results

The project was tested through manual gameplay scenarios and automated unit tests.

**Version 1 manual testing:**
- Examining and searching objects.
- Finding the brass key.
- Discovering the painting and bookshelf clues.
- Opening the drawer with the correct code.
- Obtaining the exit code.
- Completing the escape sequence.

**Version 2 manual testing:**
- Rejecting an incorrect drawer code.
- Rejecting the correct code without the required key.
- Rejecting the code when required clues have not been examined.
- Accepting the correct code when all conditions are satisfied.
- Unlocking the exit and requiring a separate door-opening action.

**Automated testing:** The game-engine test suite completed successfully with 8 tests passing.

### 8. Comparison of Both Versions

| Feature | Version 1 | Version 2 |
|---|---|---|
| Main control | Google Gemini | Python game engine |
| Interaction | Natural language | Validated actions |
| Game state | Conversation-based | Explicit state tracking |
| Rule enforcement | LLM instructions | Python validation |
| Narration | Gemini | Gemini |
| Reliability | Less predictable | More controlled |

### 9. Conclusion

The project demonstrates two approaches to developing an AI-powered interactive game. Version 1 provides flexible natural-language interaction through an LLM, while Version 2 improves reliability through explicit game-state management and rule validation.

Combining Python-based validation with AI-generated narration provides a more controlled and engaging escape-room experience.