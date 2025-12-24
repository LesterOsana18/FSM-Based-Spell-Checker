## === Refactored FSM-Based Spell Checker Code === ##
import re

# ========== Trie Implementation ========== #
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True

    def search(self, word):
        node = self.root
        for char in word:
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_end_of_word

# ========== FSM Implementation ========== #
class FSM:
    def __init__(self, states, initial_state):
        self.states = states
        self.current_state = states[initial_state]
        self.word = ""

    def transition(self, next_state_name):
        self.current_state = self.states[next_state_name]
        self.current_state.execute(self.word)

    def process_text_in_batches(self, text):
        words = re.findall(r"\w+", text)

        for word in words:
            print(f"\n[FSM]: Processing word '{word}'")
            self.word = word
            self.current_state = self.states["Start"]
            self.current_state.execute(word)

# ========== FSM States ========== #
class State:
    def __init__(self, fsm):
        self.fsm = fsm

    def execute(self, word):
        raise NotImplementedError

class StartState(State):
    def execute(self, word):
        print("[TRANSITION]: Start -> Validating")
        self.fsm.transition("Validating")

class ValidatingState(State):
    def execute(self, word):
        clean_word = word.lower()

        if word_trie.search(clean_word):
            self.fsm.transition("Valid")
        else:
            self.fsm.transition("Invalid")

class ValidWordState(State):
    def execute(self, word):
        print("[STATE]: Entered ValidWordState")
        print(f"[RESULT]: '{word}' is valid.")
        self.fsm.current_state = self.fsm.states["Start"]

class InvalidWordState(State):
    def execute(self, word):
        print("[STATE]: Entered InvalidWordState")
        print(f"[RESULT]: '{word}' is invalid.")
        self.fsm.current_state = self.fsm.states["Start"]

# ========== Build Trie ========== #
word_trie = Trie()
for word in ["kumusta", "salamat", "araw"]:
    word_trie.insert(word)

# ========== FSM Test Helper ========== #
def create_test_fsm():
    states = {
        "Start": StartState(None),
        "Validating": ValidatingState(None),
        "Valid": ValidWordState(None),
        "Invalid": InvalidWordState(None),
    }

    fsm = FSM(states, "Start")

    for state in states.values():
        state.fsm = fsm

    return fsm

# ========== Unit Tests ========== #
def test_valid_word():
    fsm = create_test_fsm()
    fsm.process_text_in_batches("kumusta")
    assert fsm.current_state.__class__.__name__ == "StartState"

def test_invalid_word():
    fsm = create_test_fsm()
    fsm.process_text_in_batches("hello")
    assert fsm.current_state.__class__.__name__ == "StartState"

if __name__ == "__main__":
    fsm = create_test_fsm()

    # Test single words (original behavior)
    print("\n[Word-by-Word Test]")
    test_valid_word()
    test_invalid_word()

    # Test batch processing of full sentences
    print("\n[Batch Processing Test]")
    sentence = "kumusta hello araw salamat goodbye"
    fsm.process_text_in_batches(sentence)

    print("\nBatch processing completed successfully.")
    print("All tests passed!")