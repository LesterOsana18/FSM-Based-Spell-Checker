# Description: This file contains the main code for the FSM-based spell checker.
# Note: This code is based on the tutorial at https://youtu.be/_nkQd9SyEpw?si=sFDhffhvPGmSAKXu.

'''
Please install the following library before running the code:
- For the Natural Language Toolkit library, go to command prompt and type the following command:

    pip install nltk
    
- Wait for the installation to finish and then you will be able to run the code.
'''

# Regular expression library
import re

# Tkinter library
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

# Natural language toolkit library
import nltk
from nltk.corpus import words 

# Function to check if the word is valid
nltk.download('words')

class SpellChecker:
    # Constructor
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("600x500")
        self.root.title("FSM-Based Spell Checker")

        self.text = ScrolledText(self.root, font=("Arial", 14))
        self.text.bind("<KeyRelease>", self.check)
        self.text.pack()

        self.old_spaces = 0

        self.root.mainloop()

    # Function to check the spelling
    def check(self, event):
        content = self.text.get("1.0", tk.END)
        space_count = content.count(" ")

        # Check if the number of spaces has changed
        if space_count != self.old_spaces:
            self.old_spaces = space_count

            # Clear all the tags
            for tag in self.text.tag_names():
                self.text.tag_delete(tag)

            for word in content.split(" "):
                # Check if the word is not in the dictionary
                if re.sub(r"[^\w]", "", word.lower()) not in words.words():
                    position = content.find(word)
                    self.text.tag_add(word, f"1.{position}", f"1.{position + len(word)}")
                    self.text.tag_config(word, foreground="red")

# Main function
SpellChecker()