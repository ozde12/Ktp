import tkinter as tk
import json

# Load the JSON data
with open('test.json', 'r') as file:
    knowledge_data = json.load(file)

# The JSON structure is expected to have two keys: "Knowledge base" and "Rules"
knowledge_base = knowledge_data["Knowledge base"]
rules = knowledge_data["Rules"]

class KnowledgeBaseApp:
    def __init__(self, root, knowledge_base, rules):
        self.root = root
        self.knowledge_base = knowledge_base
        self.rules = rules
        self.current_question = None
        self.current_feature_index = 0
        self.answers = {}
        self.current_rule_index = None  # Track the current rule index
        self.initial_features = ["backbone", "skeleton", "skull"]  # Initial feature questions
        self.initial_feature_index = 0
        self.initial_phase_complete = False  # Track if initial questions are completed
        self.setup_gui()
        print("Application initialized.")

    def setup_gui(self):
        print("Setting up GUI...")
        self.main_frame = tk.Frame(self.root, bg='#A5D6A7')
        self.main_frame.pack(fill="both", expand=True)

        self.welcome_label = tk.Label(
            self.main_frame,
            text="Welcome to the Animal Classification System!",
            bg='#A5D6A7',
            fg='black',
            font=("Arial", 40, "bold"),
            wraplength=1100
        )
        self.welcome_label.place(relx=0.5, rely=0.4, anchor="center")

        self.start_button = tk.Button(
            self.main_frame,
            text="Start",
            command=self.start,
            fg="black",
            font=("Arial", 20),
            relief="solid",
            padx=20,
            pady=10
        )
        self.start_button.place(relx=0.5, rely=0.6, anchor="center")

        self.question_label = tk.Label(
            self.main_frame,
            text="",
            bg='#A5D6A7',
            fg='black',
            font=("Arial", 40, "bold"),
            wraplength=1100
        )

        self.button_frame = tk.Frame(self.main_frame, bg='#A5D6A7')

        self.yes_button = tk.Button(
            self.button_frame,
            text="Yes",
            command=lambda: self.answer("Yes"),
            fg="black",
            font=("Arial", 17),
            relief="solid",
            padx=30,
            pady=15
        )

        self.no_button = tk.Button(
            self.button_frame,
            text="No",
            command=lambda: self.answer("No"),
            fg="black",
            font=("Arial", 17),
            relief="solid",
            padx=30,
            pady=15
        )
        print("GUI setup complete.")

    def start(self):
        print("Starting classification...")
        self.welcome_label.place_forget()
        self.start_button.place_forget()
        self.question_label.place(relx=0.5, rely=0.4, anchor="center")
        self.button_frame.place(relx=0.5, rely=0.6, anchor="center")
        self.yes_button.pack(side="left", padx=40)
        self.no_button.pack(side="right", padx=40)
        self.ask_initial_features()

    def ask_initial_features(self):
        if self.initial_feature_index < len(self.initial_features):
            feature_name = self.initial_features[self.initial_feature_index]
            question_text = self.get_question_text(feature_name)
            print(f"Asking initial feature question: {question_text}")
            self.question_label.config(text=question_text)
        else:
            print("Initial phase complete.")
            self.initial_phase_complete = True
            self.determine_initial_path()

    def get_question_text(self, feature_name):
        for group in self.knowledge_base:
            for feature in group["features"]:
                if feature["name"] == feature_name:
                    question = feature.get("question", "No question available for this feature.")
                    print(f"Found question for feature '{feature_name}': {question}")
                    return question
        print(f"No question found for feature '{feature_name}'.")
        return "No question available for this feature."

    def answer(self, user_input):
        print(f"Answer received: {user_input}")
        if not self.initial_phase_complete:
            # Process initial features
            feature_name = self.initial_features[self.initial_feature_index]
            self.answers[feature_name] = (user_input == "Yes")
            print(f"Recorded answer for '{feature_name}': {self.answers[feature_name]}")
            self.initial_feature_index += 1
            self.ask_initial_features()
        else:
            # Process main rule-based features
            feature_name = self.current_question["required features"][self.current_feature_index]
            self.answers[feature_name] = (user_input == "Yes")
            print(f"Recorded answer for '{feature_name}': {self.answers[feature_name]}")
            self.current_feature_index += 1

            if self.current_feature_index < len(self.current_question["required features"]):
                self.ask_feature_question()
            else:
                self.determine_next_step()

    def determine_initial_path(self):
        print("Determining initial path...")
        if all(self.answers.get(feature, False) for feature in self.initial_features):
            self.current_rule_index = next(
                (index for index, rule in enumerate(self.rules) if rule["current animal group"] == "vertebrates"),
                None
            )
            print("Path determined: vertebrates")
        else:
            self.current_rule_index = next(
                (index for index, rule in enumerate(self.rules) if rule["current animal group"] == "invertebrates sponge"),
                None
            )
            print("Path determined: invertebrates sponge")
        self.display_next_question()

    def display_next_question(self):
        if self.current_rule_index is not None and self.current_rule_index < len(self.rules):
            self.current_question = self.rules[self.current_rule_index]
            self.current_feature_index = 0
            print(f"Displaying next question for rule: {self.current_question}")
            self.ask_feature_question()
        else:
            print("No more rules to process. Classification is unknown.")
            self.end_classification("Unknown")

    def ask_feature_question(self):
        if self.current_feature_index < len(self.current_question["required features"]):
            feature_name = self.current_question["required features"][self.current_feature_index]
            question_text = self.get_question_text(feature_name)
            print(f"Asking feature question: {question_text}")
            self.question_label.config(text=question_text)
        else:
            self.determine_next_step()

    def determine_next_step(self):
        current_rule = self.current_question
        features = current_rule["required features"]

        yes_count = sum(self.answers.get(feature, False) for feature in features)
        print(f"Yes answers: {yes_count}/{len(features)} for current rule.")

        if yes_count >= 2:
            print(f"All required features matched. Classification: {current_rule['new direction']}")
            if current_rule["current animal group"] == current_rule["new direction"]:
                self.end_classification(f"The animal is classified as: {current_rule['new direction']}")
            else:
                next_step = current_rule["new direction"]
                print(f"Moving to next step: {next_step}")
                self.current_rule_index = next(
                    (index for index, rule in enumerate(self.rules) if rule["current animal group"] == next_step),
                    len(self.rules)
                )
                self.display_next_question()
        else:
            next_step = current_rule["else"]
            print(f"Determined next step: {next_step}")

            self.current_rule_index = next(
                (index for index, rule in enumerate(self.rules) if rule["current animal group"] == next_step),
                len(self.rules)
            )
            self.display_next_question()

    def end_classification(self, classification):
        print(f"Classification complete: {classification}")
        self.question_label.config(text=classification)
        self.yes_button.pack_forget()
        self.no_button.pack_forget()

# Initialize the app
root = tk.Tk()
app = KnowledgeBaseApp(root, knowledge_base, rules)
root.mainloop()
