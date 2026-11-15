import unittest

from game_engine import new_game_state, process_v2_action


def act(state, text):
    return process_v2_action(text, state)


class EscapeRoomEngineTests(unittest.TestCase):
    def test_wrong_drawer_code_keeps_drawer_locked(self):
        state = new_game_state()
        act(state, "Examine the desk")
        act(state, "Look at the painting")
        act(state, "Examine the bookshelf")
        result = act(state, "Enter code 1234 at drawer")
        self.assertFalse(state["drawer_open"])
        self.assertNotIn("final_code_note", state["inventory"])
        self.assertIn("INCORRECT", result["event"])

    def test_correct_drawer_code_without_key_is_rejected(self):
        state = new_game_state()
        act(state, "Look at the painting")
        act(state, "Examine the bookshelf")
        result = act(state, "Enter code 4826 at drawer")
        self.assertFalse(state["drawer_open"])
        self.assertIn("ACCESS DENIED", result["event"])

    def test_correct_key_and_code_but_skipped_clues_is_rejected(self):
        state = new_game_state()
        act(state, "Examine the desk")
        result = act(state, "Enter code 4826 at drawer")
        self.assertFalse(state["drawer_open"])
        self.assertNotIn("final_code_note", state["inventory"])
        self.assertIn("painting and the bookshelf", result["event"])

    def test_full_sequence_unlocks_then_requires_open_action(self):
        state = new_game_state()
        act(state, "Examine the desk")
        act(state, "Look at the painting")
        act(state, "Examine the bookshelf")
        result = act(state, "Enter code 4826 at drawer")
        self.assertTrue(state["drawer_open"])
        self.assertIn("final_code_note", state["inventory"])
        self.assertIn("SUCCESS", result["event"])

        result = act(state, "Enter 7319 at exit door")
        self.assertTrue(state["door_unlocked"])
        self.assertFalse(state["escaped"])
        self.assertIn("must now open", result["event"])

        result = act(state, "Open the door")
        self.assertTrue(state["escaped"])
        self.assertIn("escape", result["event"].lower())

    def test_exit_code_without_final_note_is_rejected(self):
        state = new_game_state()
        result = act(state, "Enter 7319 at exit door")
        self.assertFalse(state["door_unlocked"])
        self.assertFalse(state["escaped"])
        self.assertIn("ACCESS DENIED", result["event"])

    def test_wrong_exit_code_keeps_exit_locked(self):
        state = new_game_state()
        act(state, "Examine the desk")
        act(state, "Look at the painting")
        act(state, "Examine the bookshelf")
        act(state, "Enter 4826 at drawer")
        result = act(state, "Enter 1111 at exit door")
        self.assertFalse(state["door_unlocked"])
        self.assertFalse(state["escaped"])
        self.assertIn("INCORRECT", result["event"])

    def test_cannot_escape_by_opening_locked_door(self):
        state = new_game_state()
        result = act(state, "Open the door")
        self.assertFalse(state["door_unlocked"])
        self.assertFalse(state["escaped"])
        self.assertIn("still locked", result["event"])

    def test_cannot_escape_twice(self):
        state = new_game_state()
        act(state, "Examine the desk")
        act(state, "Look at the painting")
        act(state, "Examine the bookshelf")
        act(state, "Enter 4826 at drawer")
        act(state, "Enter 7319 at exit")
        act(state, "Open the exit door")
        result = act(state, "Open the door")
        self.assertTrue(state["escaped"])
        self.assertIn("already escaped", result["event"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
