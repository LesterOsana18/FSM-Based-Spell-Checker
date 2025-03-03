## ============================================================ ## MODULES ## ============================================================ ##
# Regular expression module
import re

# CustomTkinter module
import customtkinter as ctk
from customtkinter import *

# Tkinter module  
import tkinter as tk 
from tkinter.scrolledtext import ScrolledText 

# String matching module
from difflib import get_close_matches

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
          clean_word = re.sub(r"[^\w’'-]", "", word.lower()) # Added hyphen to allow hyphenated words

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
               # Print the resulting state and word
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

          # Initialize FSM and CustomTkinter
          self.fsm = FSM()
          self.root = ctk.CTk()  # Replace tk.Tk() with CTk
          self.root.geometry("900x600")
          self.root.title("FSM-Based Spell Checker")
          self.root.resizable(width=True, height=True)

          # Top Frame (Parent Frame)
          self.top_frame = ctk.CTkFrame(master=self.root, width=900, height=350)
          self.top_frame.pack(side="top", fill="both", expand=True)

          # Top Frame Left
          self.top_frame_left = ctk.CTkFrame(master=self.top_frame, width=600, height=350)
          self.top_frame_left.pack(side="left", fill="both", expand=True)

          # Top Frame Left Label
          self.top_frame_left_label = ctk.CTkLabel(master=self.top_frame_left, text="Tagalog Spell Checker", font=("Arial", 10), fg_color="transparent")
          self.top_frame_left_label.pack(side="top", fill="both", expand=False) 

          # Top Frame Right
          self.top_frame_right = ctk.CTkFrame(master=self.top_frame, width=300, height=350)
          self.top_frame_right.pack(side="left", fill="both", expand=True)

          # Top Frame Right Label
          self.top_frame_right_label = ctk.CTkLabel(master=self.top_frame_right, text="Spelling Suggestions", font=("Arial", 10), fg_color="transparent")
          self.top_frame_right_label.pack(side="top", fill="both", expand=False) 

          # Bottom Frame
          self.bottom_frame = ctk.CTkFrame(master=self.root, width=900, height=250)
          self.bottom_frame.pack(side="top", fill="both", expand=True)

          # Spell Checker Frame
          self.left_frame = ctk.CTkFrame(master=self.top_frame_left, width=600, height=350)
          self.left_frame.pack(side="left", fill="both", expand=True, padx=(10, 10), pady=(0, 10))

          # Configure grid for dynamic resizing
          self.left_frame.grid_rowconfigure(0, weight=1)
          self.left_frame.grid_columnconfigure(0, weight=1)  

          # Spell Checker Text Box Label
          self.sc_textbox_label = ctk.CTkLabel(master=self.left_frame, text="Start by typing or pasting your text...", font=("Arial", 12), fg_color="transparent")
          self.sc_textbox_label.grid(row=0, column=0, sticky="n", pady=(5, 10))

          # Spell Checker Text Box
          self.input_text = ctk.CTkTextbox(master=self.left_frame, width=600, height=300, font=("Arial", 14))
          self.input_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=(40, 10)) 

          # Suggestions Frame
          self.right_frame = ctk.CTkFrame(master=self.top_frame_right, width=300, height=350)
          self.right_frame.pack(side="right", fill="both", expand=True, padx=(10, 10), pady=(0, 10))

          # Configure grid for dynamic resizing
          self.right_frame.grid_rowconfigure(0, weight=1) 
          self.right_frame.grid_columnconfigure(0, weight=1)

          # Suggestions Text Box Label
          self.sg_textbox_label = ctk.CTkLabel(master=self.right_frame, text="Did you mean...", font=("Arial", 12))
          self.sg_textbox_label.grid(row=0, column=0, sticky="n", pady=(5, 10))

          # Suggestions Text Box
          self.suggestions_text = ctk.CTkTextbox(master=self.right_frame, width=230, height=250, font=("Arial", 14))
          self.suggestions_text.grid(row=0, column=0, sticky="nsew", padx=10, pady=(40, 0)) 

          # Suggestions Box Clear Button
          self.clear_button = ctk.CTkButton(master=self.right_frame, width=100, height=40, text="Clear Suggestions", font=("Arial", 10, "bold"), fg_color="red", hover_color="green", command=self.delete_suggestions)
          self.clear_button.grid(row=1, column=0, sticky="sw", padx=10, pady=(10, 10))

          # Toggle Switch for Dark Mode and Light Mode
          self.toggle_switch = ctk.CTkSwitch(master=self.right_frame, width=100, height=40, text="Dark Mode", font=("Arial", 10, "bold"), onvalue=1, offvalue=0, command=self.toggle_dark_mode)
          self.toggle_switch.grid(row=1, column=0, sticky="se", padx=10, pady=(10, 10))

          # Terminal Output Frame
          self.terminal_frame = ctk.CTkFrame(master=self.bottom_frame, width=900, height=250)
          self.terminal_frame.pack(side="bottom", fill="both", expand=True, padx=10, pady=10)

          # Terminal Output Label
          self.terminal_label = ctk.CTkLabel(master=self.terminal_frame, text="Terminal Output", font=("Arial", 12))
          self.terminal_label.pack(side="top", fill="x", expand=False, pady=(5, 5))

          # Terminal Output Text Box
          self.terminal_output = ctk.CTkTextbox(master=self.terminal_frame, font=("Courier New", 16), fg_color="black", state="disabled")
          self.terminal_output.pack(fill="both", expand=True)

          # Redirect stdout and stderr to terminal_output
          sys.stdout = TextRedirector(self.terminal_output, "stdout")
          sys.stderr = TextRedirector(self.terminal_output, "stderr")
          self.terminal_output.tag_config("stdout", foreground="white")
          self.terminal_output.tag_config("stderr", foreground="red")

          # Bind the click event to invalid words only
          self.input_text.tag_bind("invalid", "<Button-1>", self.handle_click)
          
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

     # Highlight word method
     def highlight_word(self, word, start_pos, end_pos, is_invalid):
          # Highlight a word as valid or invalid.
          self.input_text.tag_remove("invalid", start_pos, end_pos)  # Remove previous invalid tags
          self.input_text.tag_remove("valid", start_pos, end_pos)    # Remove previous valid tags

          if is_invalid:
               self.input_text.tag_add("invalid", start_pos, end_pos)
               self.input_text.tag_config("invalid", foreground="red")
     
     # Handle click method
     def handle_click(self, event):
          """Handle left mouse clicks only on invalid words."""
          try:
               # Get the index of the clicked position
               click_index = self.input_text.index(f"@{event.x},{event.y}")

               # Get the tags associated with the clicked position
               tags = self.input_text.tag_names(click_index)

               # Check if the "invalid" tag is present
               if "invalid" in tags:
                    # Get the word at the clicked position
                    word_start = self.input_text.index(f"{click_index} wordstart")
                    word_end = self.input_text.index(f"{click_index} wordend")
                    clicked_word = self.input_text.get(word_start, word_end).strip()

                    # Display suggestions in the suggestion box
                    suggestions = self.get_suggestions(clicked_word)
                    self.delete_suggestions()
                    self.suggestions_text.configure(state="normal")

                    if suggestions:
                         self.suggestions_text.insert(tk.END, f"Suggestions for '{clicked_word}':\n")
                         for suggestion in suggestions:
                              self.suggestions_text.insert(tk.END, f"• {suggestion}\n")
                    else:
                         self.suggestions_text.insert(tk.END, f"No suggestions for '{clicked_word}'.\n")
                    
                    self.suggestions_text.configure(state="disabled")
          except Exception as e:
               print(f"Error in handle_click: {e}")

     # Get suggestions method
     def get_suggestions(self, word):
          """Retrieve suggestions for the given word."""
          return get_close_matches(word, word_set, n=5, cutoff=0.6)

     # Delete suggestions method
     def delete_suggestions(self):
          """Delete suggestions from the suggestion box."""
          self.suggestions_text.configure(state="normal")
          self.suggestions_text.delete("1.0", tk.END)
          self.suggestions_text.configure(state="disabled")

     # Toggle dark mode method
     def toggle_dark_mode(self):
          val = self.toggle_switch.get()
          if val:
               # Set dark mode
               self.root._set_appearance_mode("dark")

               # Set dark mode for all widgets
               self.top_frame._set_appearance_mode("dark")
               self.top_frame_left._set_appearance_mode("dark")
               self.top_frame_right._set_appearance_mode("dark")
               self.bottom_frame._set_appearance_mode("dark")

               self.left_frame._set_appearance_mode("dark")
               self.right_frame._set_appearance_mode("dark")
               
               self.input_text._set_appearance_mode("dark")
               self.suggestions_text._set_appearance_mode("dark")
               self.terminal_frame._set_appearance_mode("dark")
               self.terminal_output._set_appearance_mode("dark")

               self.top_frame_left_label._set_appearance_mode("dark")
               self.top_frame_right_label._set_appearance_mode("dark")
               self.sc_textbox_label._set_appearance_mode("dark")
               self.sg_textbox_label._set_appearance_mode("dark")
               self.terminal_label._set_appearance_mode("dark")

               self.clear_button._set_appearance_mode("dark")
               self.toggle_switch._set_appearance_mode("dark")
          else:
               # Set light mode
               self.root._set_appearance_mode("light")

               # Set light mode for all widgets
               self.top_frame._set_appearance_mode("light")
               self.top_frame_left._set_appearance_mode("light")
               self.top_frame_right._set_appearance_mode("light")
               self.bottom_frame._set_appearance_mode("light")

               self.left_frame._set_appearance_mode("light")
               self.right_frame._set_appearance_mode("light")
               
               self.input_text._set_appearance_mode("light")
               self.suggestions_text._set_appearance_mode("light")
               self.terminal_frame._set_appearance_mode("light")
               self.terminal_output._set_appearance_mode("light")

               self.top_frame_left_label._set_appearance_mode("light")
               self.top_frame_right_label._set_appearance_mode("light")
               self.sc_textbox_label._set_appearance_mode("light")
               self.sg_textbox_label._set_appearance_mode("light")
               self.terminal_label._set_appearance_mode("light")

               self.clear_button._set_appearance_mode("light")
               self.toggle_switch._set_appearance_mode("light")

     # Manual check method
     def manual_check(self, event):
          """Manually check the validity of words and show suggestions for invalid words."""
          # Get the current content of the text widget
          content = self.input_text.get("1.0", tk.END).strip()

          # Trigger on space or Enter key
          if event.keysym in ("space", "Return"):
               words = content.split()

               # Extract the last word, clean it, and process
               if words and len(words[-1]) > 1:  # Only process words longer than one character
                    last_word = words[-1]
                    clean_word = re.sub(r"[^\w’'-]", "", last_word.lower()) # Allow ’, ', and hyphens

                    # Find the start and end positions of the word
                    start_pos = content.rfind(last_word)
                    end_pos = start_pos + len(last_word)

                    # Calculate line and column positions for multi-line text
                    line_start = content[:start_pos].count('\n') + 1
                    col_start = start_pos - content.rfind('\n', 0, start_pos) - 1
                    line_end = content[:end_pos].count('\n') + 1
                    col_end = end_pos - content.rfind('\n', 0, end_pos) - 1
                    
                    # Highlight invalid words in red and valid words in black
                    self.highlight_word(last_word, f"{line_start}.{col_start}", f"{line_end}.{col_end}", clean_word not in word_set)

                    # Execute FSM for the word
                    self.fsm.execute(last_word)
                    self.processed_words.add(last_word)
     
     # Automatic check method
     def automatic_check(self, event):
          # Get the current content of the text widget
          content = self.input_text.get("1.0", tk.END).strip()

          # Detect paste: Check if multiple spaces are added at once
          if event.keysym == "Control_L" or len(content.split()) > len(self.processed_words):
               self.processed_words.clear()  # Clear previously processed words
               self.invalid_words = []  # Add a list to store and track invalid words

               # Process each word in the pasted text
               for word in content.split():
                    clean_word = re.sub(r"[^\w'’\-]", "", word.lower())  # Allow hyphens
                    start_pos = content.find(word)
                    end_pos = start_pos + len(word)

                    # Calculate line and column positions for multi-line text
                    line_start = content[:start_pos].count('\n') + 1
                    col_start = start_pos - content.rfind('\n', 0, start_pos) - 1
                    line_end = content[:end_pos].count('\n') + 1
                    col_end = end_pos - content.rfind('\n', 0, end_pos) - 1

                    # Highlight invalid words
                    self.highlight_word(word, f"{line_start}.{col_start}", f"{line_end}.{col_end}", clean_word not in word_set)

                    # Run FSM for the current word
                    self.fsm.execute(word)

               # Save the initial state of words in the pasted text
               self.processed_words = set(content.split())

               # Start monitoring for edits
               self.monitor_edits()

     def monitor_edits(self):
          """Monitor edits in the text widget and run FSM for edited words."""
          # Get the current content of the text widget
          current_content = self.input_text.get("1.0", tk.END).strip()
          current_words = {}
               
          # Build a dictionary of words with their positions
          for match in re.finditer(r"(?:^|(?<=\s))['’\-]*[\w]+(?:['’\-]+[\w]+)*['’\-]*(?=$|\s)", current_content):
               word = match.group()
               start_pos = match.start()
               current_words[start_pos] = word

          # Compare current words with previously processed words
          edited_words = {
               pos: word for pos, word in current_words.items()
               if pos not in self.processed_words or self.processed_words.get(pos) != word
          }

          # Process only the edited words
          if edited_words:
               for start_pos, word in edited_words.items():
                    clean_word = re.sub(r"[^\w'’\-]", "", word.lower())  # Allow hyphens and apostrophes
                    end_pos = start_pos + len(word)

                    # Calculate line and column positions
                    line_start = current_content[:start_pos].count('\n') + 1
                    col_start = start_pos - current_content.rfind('\n', 0, start_pos) - 1
                    line_end = current_content[:end_pos].count('\n') + 1
                    col_end = end_pos - current_content.rfind('\n', 0, end_pos) - 1

                    # Highlight the word and execute FSM
                    self.highlight_word(word, f"{line_start}.{col_start}", f"{line_end}.{col_end}", clean_word not in word_set)
                    self.fsm.execute(word)

          # Update processed words with current positions and content
          self.processed_words = current_words

          # Continue monitoring after a short delay
          self.input_text.after(100, self.monitor_edits)     

## ============================================================ ## RUN THE APPLICATION ## ============================================================ ##
if __name__ == "__main__":
     spell_checker = SpellChecker()