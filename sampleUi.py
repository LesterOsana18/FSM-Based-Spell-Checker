## ============================================================ ## MODULES ## ============================================================ ##
# Regular expression module
import re

# Tkinter module  
import tkinter as tk 
from tkinter.scrolledtext import ScrolledText 

# Logging module
import logging

# os module to ensure that the program can access the filipino_dict.txt file
import os

# Storing the file path of the filipino words list
file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "filipino_dict.txt")

# Loading the file
def load_filipino_word_list(file_path):
     try:
          with open(file_path, "r", encoding="utf-8") as file:
               return set(file.read().splitlines())
     except FileNotFoundError:
          print(f"File '{file_path}' not found. Using an empty word set.")
          return set()

# Setting word_set as the Filipino word list
word_set = load_filipino_word_list(file_path)

import sys
import atexit

## ============================================================ ## TEXT REDIRECTOR CLASS ## ============================================================ ##
# Redirects terminal output to the text widget
class TextRedirector:
     def __init__(self, text_widget, tag="stdout"):
          self.text_widget = text_widget
          self.tag = tag

     def write(self, text):
          self.text_widget.configure(state="normal")  # Enable editing
          self.text_widget.insert(tk.END, text, (self.tag,))
          self.text_widget.configure(state="disabled")  # Disable editing to mimic a terminal
          self.text_widget.see(tk.END)  # Scroll to the end

     def flush(self):
          pass  # No need for explicit flushing

# Reset output to sys.stdout and sys.stderr
@atexit.register
def reset_output():
     sys.stdout = sys.__stdout__
     sys.stderr = sys.__stderr__

## ============================================================ ## FSM STATE BASE CLASS ## ============================================================ ##
class State:
     # Constructor
     def __init__(self, fsm):
          self.fsm = fsm

     # Execute method
     def execute(self, word):
          pass

## ============================================================ ## FSM STATES ## ============================================================ ##
class StartState(State):
     # Execute method
     def execute(self, word):
          print("\n[TRANSITION]: Start -> Validating")
          clean_word = re.sub(r"[^\w-]", "", word.lower()) # Added hyphen to allow hyphenated words

          if clean_word in word_set:
               print("[TRANSITION]: Validating -> Valid")
               try:
                    # Add preconditions or additional checks here
                    if self.can_transition_to_valid(clean_word):
                         self.fsm.transition("valid", word)  # Pass the word to transition
                    else:
                         print("Preconditions not met for transition to 'valid'")
               except Exception as e:
                    logging.error(f"Error during transition to 'valid': {e}")
          else:
               print("[TRANSITION]: Validating -> Invalid")
               self.fsm.transition("invalid", word)  # Pass the word to transition

     # Additional checks method
     def can_transition_to_valid(self, word):
          return True
     
class ValidWordState(State):
     def execute(self, word):
          # Placeholder for valid word processing
          pass

class InvalidWordState(State):
     def execute(self, word):
          # Placeholder for invalid word processing
          pass

## ============================================================ ## FSM CLASS ## ============================================================ ##
class FSM:
     # Constructor
     def __init__(self):
          # Initialize states
          self.states = {
               "start": StartState(self),
               "valid": ValidWordState(self),
               "invalid": InvalidWordState(self)
          }
          # Set the initial state
          self.current_state = self.states["start"]
          self.text_widget = None 

     # Transition method
     def transition(self, state_name, word=None):
          if state_name in self.states:
               # Suppress the "Switching to State: Start" message
               if state_name != "start" and word:
                    print(f"[RESULTING STATE]: {state_name.capitalize()}", flush=True)
                    print(f"[WORD]: {word}", flush=True)
               self.current_state = self.states[state_name]
          else:
               # Print error message if state does not exist
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
               # Get the current content of the text widget
               content = self.text_widget.get("1.0", tk.END)
               start_index = "1.0"
               word_length = len(word)
               # Find and highlight the word in the text widget
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

## ============================================================ ## MAIN FUNCTION ## ============================================================ ##
class SpellChecker:
     # Constructor
     def __init__(self):
          # User input
          print("\n---------- FSM-Based Spell Checker ----------")
          print("[INSTRUCTIONS] Please select an option below:")
          print("[1] Enter text manually")
          print("[0] Paste text")
          user_input = input("[SELECT] Enter [1] or [0] only: ")

          # Initialize FSM and Tkinter
          self.fsm = FSM()
          self.root = tk.Tk()
          self.root.geometry("900x600")
          self.root.title("FSM-Based Spell Checker")
          
          # Create a PanedWindow for resizable areas
          self.vertical_main_window = tk.PanedWindow(self.root, orient="vertical")
          self.vertical_main_window.pack(fill=tk.BOTH, expand=True)
          
          # Create a second PanedWindow for the left and right frames (horizontal resizing)
          self.horizontal_top_pane = tk.PanedWindow(self.vertical_main_window, orient="horizontal")
          self.vertical_main_window.add(self.horizontal_top_pane, stretch="always")

          # Left frame for user input text
          self.left_frame = tk.LabelFrame(self.horizontal_top_pane, text="Tagalog Spell Checker", padx=5, pady=5, width=600, height=400)
          self.horizontal_top_pane.add(self.left_frame, width=600)
          
          self.input_label = tk.Label(self.left_frame, text="Start by typing or pasting your text...", font=("Arial", 8))
          self.input_label.pack(fill=tk.BOTH, expand=True)

          # Right frame for suggestions
          self.right_frame = tk.LabelFrame(self.horizontal_top_pane, text="Spelling Suggestions", padx=5, pady=5, width=300, height=400)
          self.horizontal_top_pane.add(self.right_frame, width=300)
          
          self.placeholder_label = tk.Label(self.right_frame, text="Did you mean...", font=("Arial", 8))
          self.placeholder_label.pack(fill=tk.BOTH, expand=True)

          # Bottom frame for terminal output
          self.bottom_frame = tk.LabelFrame(self.vertical_main_window, text="Terminal Output", padx=5, pady=5, width=900, height=200)
          self.vertical_main_window.add(self.bottom_frame, height=200, stretch="always")

          # Text widget for user input (left section)
          self.input_text = ScrolledText(self.left_frame, font=("Arial", 11))
          self.input_text.pack(fill=tk.BOTH, expand=True)

          # Placeholder for suggestions (right section)
          self.suggestions_text = ScrolledText(self.right_frame, font=("Arial", 10), state="disabled")
          self.suggestions_text.pack(fill=tk.BOTH, expand=True)

          # Text widget for terminal output (bottom section)
          self.terminal_output = ScrolledText(self.bottom_frame, font=("Courier New", 9), bg="black", fg="white", state="disabled")
          self.terminal_output.pack(fill=tk.BOTH, expand=True)
          
          # Redirect stdout and stderr to terminal_output
          sys.stdout = TextRedirector(self.terminal_output, "stdout")
          sys.stderr = TextRedirector(self.terminal_output, "stderr")
          self.terminal_output.tag_config("stdout", foreground="white")
          self.terminal_output.tag_config("stderr", foreground="red")
          
          # Bind text widget to manual or automatic check
          if user_input == "1":
               self.input_text.bind("<KeyRelease>", self.manual_check)
          elif user_input == "0":
               self.input_text.bind("<KeyRelease>", self.automatic_check)
          else:   
               sys.__stdout__.write("[ERROR] Invalid option. Please enter [1] or [0] only.\n") # Bypass text redirection and print directly on the terminal
               self.root.destroy()
               return
          print("\n[STATUS]: FSM-Based Spell Checker is running...")

          # Set widgets for FSM
          self.fsm.set_text_widget(self.input_text)
          self.old_spaces = 0
          self.processed_words = set()  # Track already processed words
          self.root.mainloop()

     # Manual check method 
     def manual_check(self, event):
          # Get the current content of the text widget
          content = self.input_text.get("1.0", tk.END).strip()

          # Detect typing: Check if words are being typed one by one
          if event.keysym in ("space", "Return"):
               words = content.split()
               
               # Extract the last word, clean it, and find its start and end positions in the content
               if words and len(words[-1]) > 1:
                    last_word = words[-1]
                    clean_word = re.sub(r"[^\w-]", "", last_word.lower())  # Allow hyphens
                    start_pos = content.rfind(last_word)
                    end_pos = start_pos + len(last_word)

                    # Calculate the line and column positions
                    line_start = content[:start_pos].count('\n') + 1
                    col_start = start_pos - content.rfind('\n', 0, start_pos) - 1
                    line_end = content[:end_pos].count('\n') + 1
                    col_end = end_pos - content.rfind('\n', 0, end_pos) - 1

                    # Highlight invalid words
                    if clean_word not in word_set:
                         self.input_text.tag_add(f"invalid_{start_pos}", f"{line_start}.{col_start}", f"{line_end}.{col_end}")
                         self.input_text.tag_config(f"invalid_{start_pos}", foreground="red")
                    
                    # Revert the color of corrected (valid) words to black
                    elif clean_word in word_set:
                         self.input_text.tag_add(f"valid_{start_pos}", f"{line_start}.{col_start}", f"{line_end}.{col_end}")
                         self.input_text.tag_config(f"valid_{start_pos}", foreground="black")

                    self.fsm.execute(last_word)
                    self.processed_words.add(last_word)

     # Automatic check method
     def automatic_check(self, event):
          # Get the current content of the text widget
          content = self.input_text.get("1.0", tk.END).strip()

          # Detect paste: Check if multiple spaces are added at once
          if event.keysym == "Control_L" or len(content.split()) > len(self.processed_words):
               self.processed_words.clear()  # Clear previously processed words
               for word in content.split():
                    clean_word = re.sub(r"[^\w-]", "", word.lower())  # Allow hyphens
                    start_pos = content.find(word)
                    end_pos = start_pos + len(word)

                    # Highlight invalid words
                    if clean_word not in word_set:
                         self.input_text.tag_add(f"invalid_{start_pos}", f"1.{start_pos}", f"1.{end_pos}")
                         self.input_text.tag_config(f"invalid_{start_pos}", foreground="red")

                    # Execute FSM for each word
                    self.fsm.execute(word)

               # Update processed words
               self.processed_words = set(content.split())
               return

## ============================================================ ## RUN THE APPLICATION ## ============================================================ ##
if __name__ == "__main__":
     spell_checker = SpellChecker()