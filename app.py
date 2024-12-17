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
        # Get the content of the text widget
        content = self.text.get("1.0", tk.END)
        space_count = content.count(" ")
        
        # Check if the number of spaces has changed
        if space_count != self.old_spaces:
            self.old_spaces = space_count
            for tag in self.text.tag_names():
                self.text.tag_delete(tag)

            # Iterate over words in the text
            current_index = 0
            for word in content.split(" "):
                clean_word = re.sub(r"[^\w]", "", word.lower())
                if clean_word:
                    if clean_word not in word_set:
                        position = content.find(word, current_index)
                        start_pos = f"1.{position}"
                        end_pos = f"1.{position + len(word)}"
                        tag_name = f"invalid_{position}"
                        self.text.tag_add(tag_name, start_pos, end_pos)
                        self.text.tag_config(tag_name, foreground="red")
                    self.fsm.execute(word)
                current_index += len(word) + 1  # +1 for the space

## ============================================================ ##

# Run the application
if __name__ == "__main__":
    spell_checker = SpellChecker()