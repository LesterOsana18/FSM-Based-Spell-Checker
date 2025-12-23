## === Refactored FSM-Based Spell Checker Code === ##
import re

class FSM:
    def __init__(self, states, initial_state):
        self.states = states
        self.current_state = states[initial_state]
        self.transition_log = []  # Logs transitions for the current input
        self.all_logs = []  # Stores all logs across inputs
        self.buffer = ""  # Accumulates letters to form the complete word

    def transition(self, next_state_name, word_or_letter):
        current_state_name = self.current_state.__class__.__name__
        self.transition_log.append(
            f"Transition: {current_state_name} -> {next_state_name} | Input: '{word_or_letter}'"
        )
        self.current_state = self.states[next_state_name]
        self.current_state.execute(word_or_letter)

    def process_text_by_letter(self, text):
        """
        Process the input text letter by letter through the FSM.
        :param text: The input string to process.
        """
        for index, char in enumerate(text):
            print(f"[FSM]: Processing letter {index + 1}/{len(text)}: '{char}'")
            self.buffer += char  # Accumulate letters into the buffer

            # Pass the current state and full buffer for validation
            self.current_state.execute(self.buffer)

    def print_transition_log(self):
        """ Display the logged FSM transitions, then reset the log. """
        print("\n[FSM LOG]")
        for entry in self.transition_log:
            print(entry)
        print("[END LOG]\n")
        self.all_logs.append(self.transition_log)  # Save current log for history
        self.transition_log = []  # Clear the current log


class State:
    def __init__(self, fsm):
        self.fsm = fsm

    def execute(self, word):
        raise NotImplementedError()


class StartState(State):
    def execute(self, word):
        # Validate once we encounter a complete word (spaces/punctuation indicate word boundaries)
        if self.is_complete_word(word):
            print("[TRANSITION]: Start -> Validating")
            clean_word = re.sub(r"[^\w’'-]", "", word.lower())
            if clean_word in word_set:
                self.fsm.transition("Valid", clean_word)  # Pass full, cleaned word to next state
            else:
                self.fsm.transition("Invalid", clean_word)

    def is_complete_word(self, word):
        # Check if the word ends with a space or punctuation
        return bool(re.search(r"\s|[.!?]$", word))


class ValidWordState(State):
    def execute(self, word):
        # Ensure full word processing before marking it valid
        if self.fsm.buffer.strip() == word.strip():  # Check buffer matches current word context
            print(f"[STATE]: '{word.strip()}' is valid!\n")
            self.fsm.buffer = ""  # Clear the buffer after full word validation


class InvalidWordState(State):
    def execute(self, word):
        print(f"[STATE]: '{word.strip()}' is invalid!\n")
        self.fsm.buffer = ""  # Clear the buffer after validation


# Test Words
word_set = {"kumusta", "salamat", "araw"}


def create_test_fsm():
    states = {
        "Start": StartState(None),
        "Valid": ValidWordState(None),
        "Invalid": InvalidWordState(None),
    }
    fsm = FSM(states, "Start")
    for state in fsm.states.values():
        state.fsm = fsm
    return fsm


# Unit Tests
def test_valid_word():
    fsm = create_test_fsm()
    fsm.process_text_by_letter("kumusta ")
    assert fsm.current_state.__class__.__name__ == "ValidWordState"

def test_invalid_word():
    fsm = create_test_fsm()
    fsm.process_text_by_letter("hello!")
    assert fsm.current_state.__class__.__name__ == "InvalidWordState"


if __name__ == "__main__":
    fsm = create_test_fsm()

    # Run Unit Tests
    test_valid_word()
    test_invalid_word()
    print("All tests passed!")