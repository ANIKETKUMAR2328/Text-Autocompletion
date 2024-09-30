import re
import tkinter as tk
from tkinter import StringVar, Listbox, Scrollbar


def levenshtein_distance(s1, s2):
    """Calculates the Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    # If one of the strings is empty
    if len(s2) == 0:
        return len(s1)

    # Initialize the distance matrix
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


class PrefixAutocomplete:
    def __init__(self):
        self.words_list = set()  # Initialize an empty set for storing words

    def train(self, text):
        # Tokenize words and add them to the set
        words = re.findall(r'\b\w+\b', text.lower())  # Extract words
        self.words_list.update(words)

    def predict(self, prefix):
        prefix = prefix.lower()
        exact_matches = [word for word in self.words_list if word.startswith(prefix)]

        # Fuzzy match only if no exact matches are found
        if not exact_matches:
            # Set a maximum distance threshold for fuzzy matching
            max_distance = 2  # Allow up to 2 changes
            fuzzy_matches = [
                word for word in self.words_list if levenshtein_distance(prefix, word) <= max_distance
            ]
            fuzzy_matches = sorted(fuzzy_matches, key=lambda word: levenshtein_distance(prefix, word))
            return fuzzy_matches[:10]  # Return top 10 fuzzy matches

        return exact_matches[:10]  # Return top 10 exact matches


class AutocompleteApp:
    def __init__(self, root, autocomplete_model):
        self.model = autocomplete_model
        self.root = root
        self.root.title("Autocomplete Example")

        # GUI Elements
        self.entry_text = StringVar()
        self.entry = tk.Entry(root, textvariable=self.entry_text, width=50)
        self.entry.pack()

        # Bind key release to update suggestions
        self.entry_text.trace("w", self.on_key_release)

        self.suggestions_listbox = Listbox(root, width=50, height=10)
        self.suggestions_listbox.pack()

        # Add scrollbar for the listbox
        self.scrollbar = Scrollbar(root)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.suggestions_listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.suggestions_listbox.yview)

    def on_key_release(self, *args):
        # Get the current text from the input box
        prefix = self.entry_text.get()

        # Fetch the predictions based on the prefix
        predictions = self.model.predict(prefix)

        # Update the suggestions in the listbox
        self.update_suggestions(predictions)

    def update_suggestions(self, suggestions):
        # Clear the current suggestions
        self.suggestions_listbox.delete(0, tk.END)

        # Insert new suggestions into the listbox
        for suggestion in suggestions:
            self.suggestions_listbox.insert(tk.END, suggestion)


# Custom dataset (you can replace this with your own dataset or read from a file)
sample_text = """
apple aroma arm artist angry amusement awesome airplane ant algorithm angle ankle anchor answer article animal animation actor adventure alarm alphabet arena armor attic arrow asset attempt attitude altitude atom area action ability absence abundance abc acc
"""

# Initialize the autocomplete model and train it with the custom dataset
autocomplete_model = PrefixAutocomplete()
autocomplete_model.train(sample_text)

# Create the root window for the GUI
root = tk.Tk()

# Initialize the autocomplete app with the GUI and the model
app = AutocompleteApp(root, autocomplete_model)

# Run the tkinter main loop
root.mainloop()
