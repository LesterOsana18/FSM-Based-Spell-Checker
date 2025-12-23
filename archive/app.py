# Regular expression module
import re

# Tkinter module  
import tkinter as tk 
from tkinter.scrolledtext import ScrolledText

# Natural Language Toolkit module
import nltk
from nltk.corpus import words

# Download NLTK word list
nltk.download('words')

# Optimize word lookup
word_set = set(words.words()) 

# Logging module
import logging

## ============================================================ ##

# FSM State Base Class
class State:
    # Constructor
    def __init__(self, fsm):
        self.fsm = fsm

    # Execute method
    def execute(self, word):
        pass

## ============================================================ ##

# FSM States
class StartState(State):
    # Execute method
    def execute(self, word):
        print("\n[TRANSITION]: Start -> Validating")
        clean_word = re.sub(r"[^\w]", "", word.lower())
        if clean_word in word_set:
            print("[TRANSITION]: Validating -> Valid")
            try:
                # Add preconditions or additional checks here
                if self.can_transition_to_valid(clean_word):
                    self.fsm.transition("valid")
                else:
                    print("Preconditions not met for transition to 'valid'")
            except Exception as e:
                logging.error(f"Error during transition to 'valid': {e}")
        else:
            print("[TRANSITION]: Validating -> Invalid")
            self.fsm.transition("invalid")

    def can_transition_to_valid(self, word):
        # Add any additional checks needed before transitioning
        return True  # Replace with actual checks
    
class ValidWordState(State):
    def execute(self, word):
        print(f"State: Valid | Word: {word}")

class InvalidWordState(State):
    def execute(self, word):
        print(f"State: Invalid | Word: {word}")

## ============================================================ ##

# FSM Class
class FSM:
    # Constructor
    def __init__(self):
        self.states = {
            "start": StartState(self),
            "valid": ValidWordState(self),
            "invalid": InvalidWordState(self)
        }
        self.current_state = self.states["start"]
        self.text_widget = None  # Initialize text_widget to None

    # Transition method
    def transition(self, state_name):
        if state_name in self.states:
            # Suppress the "Switching to State: Start" message
            if state_name != "start":
                print(f"[RESULTING STATE]: {state_name.capitalize()}", flush=True)
            self.current_state = self.states[state_name]
        else:
            print(f"Error: State '{state_name}' does not exist", flush=True)

    # Execute method
    def execute(self, word):
        self.current_state.execute(word)
        self.transition("start")  # Always reset to StartState after processing a word

    # Set text widget method
    def set_text_widget(self, text_widget):
        self.text_widget = text_widget

    # Highlight word method
    def highlight_word(self, word):
        if self.text_widget:
            content = self.text_widget.get("1.0", tk.END)
            start_index = "1.0"  # Start from the beginning of the text
            word_length = len(word)
            while True:
                start_index = self.text_widget.search(word, start_index, stop_index=tk.END, regexp=False)
                if not start_index:
                    break
                end_index = f"{start_index} + {word_length}c"
                tag_name = f"invalid_{start_index.replace('.', '_')}"
                self.text_widget.tag_add(tag_name, start_index, end_index)
                self.text_widget.tag_config(tag_name, foreground="red")
                start_index = end_index
        else:
            print("Error: Text widget is not set", flush=True)

## ============================================================ ##

# Main Application
class SpellChecker:
    # Constructor
    def __init__(self):
        self.fsm = FSM()
        self.root = tk.Tk()
        self.root.geometry("800x500")
        self.root.title("FSM-Based Spell Checker")

        # Text input widget
        self.text = ScrolledText(self.root, font=("Arial", 14))
        self.text.bind("<KeyRelease>", self.check)
        self.text.pack()

        # Set widgets for FSM
        self.fsm.set_text_widget(self.text)

        self.old_spaces = 0
        self.processed_words = set()  # Track already processed words
        self.root.mainloop()

    # Check method
    def check(self, event):
        # Get the current content of the text widget
        content = self.text.get("1.0", tk.END).strip()

        # Detect paste: Check if multiple spaces are added at once
        if event.keysym == "Control_L" or len(content.split()) > len(self.processed_words):
            self.processed_words.clear()  # Clear previously processed words
            for word in content.split():
                clean_word = re.sub(r"[^\w]", "", word.lower())
                start_pos = content.find(word)
                end_pos = start_pos + len(word)

                # Highlight invalid words
                if clean_word not in word_set:
                    self.text.tag_add(f"invalid_{start_pos}", f"1.{start_pos}", f"1.{end_pos}")
                    self.text.tag_config(f"invalid_{start_pos}", foreground="red")

                # Execute FSM for each word
                self.fsm.execute(word)

            # Update processed words
            self.processed_words = set(content.split())
            return

        # Handle typing: Trigger validation only when space or Enter is pressed
        if event.keysym not in ("space", "Return"):
            return

        # Validate the last word typed
        words = content.split()
        if not words:
            return  # No words to process
        last_word = words[-1]  # Get the last word typed

        # Clean the word for validation
        clean_word = re.sub(r"[^\w]", "", last_word.lower())
        start_pos = content.rfind(last_word)
        end_pos = start_pos + len(last_word)

        # Highlight invalid words
        if clean_word not in word_set:
            self.text.tag_add(f"invalid_{start_pos}", f"1.{start_pos}", f"1.{end_pos}")
            self.text.tag_config(f"invalid_{start_pos}", foreground="red")

        # Execute FSM for the last word
        self.fsm.execute(last_word)

        # Add last word to processed words
        self.processed_words.add(last_word)

## ============================================================ ##

# Run the application
if __name__ == "__main__":
    spell_checker = SpellChecker()