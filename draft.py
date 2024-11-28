import tkinter as tk
import json

# Load the JSON data
with open('knowledge_base.json', 'r') as file:
    knowledge_data = json.load(file)

# Extract relevant sections from the JSON
knowledge_base = knowledge_data["Knowledge base"]
rules = knowledge_data["Rules"]
facts = knowledge_data["Facts"]

class KnowledgeBaseApp:
    def __init__(self, root, knowledge_base, rules):
        self.root = root
        self.knowledge_base = knowledge_base
        self.rules = rules
        self.current_question = None
        self.current_group = "animal"  # Start with the general category
        self.answers = {}  # Store user answers
        self.setup_gui()
        self.start()

    def setup_gui(self):
        self.main_frame = tk.Frame(self.root, bg='white')
        self.main_frame.pack(fill="both", expand=True)
        self.question_label = tk.Label(
            self.main_frame,
            text="",
            bg='white',  # Background color
            fg='black',  # Text color
            font=("Arial", 14),
            wraplength=500
        )
        self.question_label.pack(pady=20)
        self.yes_button = tk.Button(self.main_frame, text="Yes", command=lambda: self.answer("Yes"))
        self.yes_button.pack(side="left", padx=20)
        self.no_button = tk.Button(self.main_frame, text="No", command=lambda: self.answer("No"))
        self.no_button.pack(side="right", padx=20)


    def start(self):
        self.display_next_question("1 and 2")  # Starting with the first set of questions

    def display_next_question(self, question_number):
        for rule in self.rules:
            if rule["question number"] == question_number:
                self.current_question = rule
                features = rule["features"]
                self.question_label.config(text=" and ".join([self.get_question_text(feature) for feature in features]))
                return
        self.end_classification("No matching rule found.")

    def get_question_text(self, feature_name):
        for group in self.knowledge_base:
            for feature in group["features"]:
                if feature["name"] == feature_name:
                    return feature["question"]
        return "Unknown question"

    def answer(self, user_input):
        answers = self.current_question
        if len(answers["features"]) == 1:  # Single feature question
            next_step = answers["true"] if user_input == "Yes" else answers["false"]
        else:  # Multiple feature question
            if user_input == "Yes":
                self.answers[self.current_question["features"][0]] = True
            else:
                self.answers[self.current_question["features"][0]] = False

            next_step = answers.get("bothTrue") if all(self.answers.values()) else (
                answers.get("bothFalse") if not any(self.answers.values()) else answers.get("oneTrue"))

        if next_step in [group["animal group"] for group in self.knowledge_base]:  # Classification found
            self.end_classification(next_step)
        else:
            self.display_next_question(next_step)

    def end_classification(self, classification):
        self.question_label.config(text=f"The animal is classified as: {classification}")
        self.yes_button.pack_forget()
        self.no_button.pack_forget()

# Initialize the app
root = tk.Tk()
app = KnowledgeBaseApp(root, knowledge_base, rules)
root.mainloop()
