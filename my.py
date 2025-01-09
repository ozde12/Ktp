import tkinter as tk
import json

# Load the JSON data
with open('knowledge_base.json', 'r') as file:
    knowledge_data = json.load(file)

knowledge_base = knowledge_data["Knowledge base"]
rules = knowledge_data["Rules"]

class KnowledgeBaseApp:
    def __init__(self, root, knowledge_base, rules):
        self.root = root
        self.knowledge_base = knowledge_base
        self.rules = rules
        self.current_rule_index = None
        self.current_feature_index = 0
        self.answers = {}
        self.current_question = None
        self.setup_gui()
        print("KnowledgeBaseApp initialized.")

    def setup_gui(self):
        print("Setting up GUI...")
        self.main_frame = tk.Frame(self.root, bg='#A5D6A7')
        self.main_frame.pack(fill="both", expand=True)

        self.root.geometry("1200x800")
        self.root.title("Animal Classification System")

        self.question_label = tk.Label(
            self.main_frame,
            text="Welcome to the Animal Classification System!",
            bg='#A5D6A7',
            fg='black',
            font=("Arial", 30, "bold"),
            wraplength=1100
        )
        self.question_label.place(relx=0.5, rely=0.4, anchor="center")

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
        print("Start button clicked. Beginning classification...")
        self.start_button.place_forget()
        self.button_frame.place(relx=0.5, rely=0.6, anchor="center")
        self.yes_button.pack(side="left", padx=40)
        self.no_button.pack(side="right", padx=40)
        self.current_rule_index = 0
        self.display_next_question()

    def display_next_question(self):
        if self.current_rule_index is not None and self.current_rule_index < len(self.rules):
            self.current_question = self.rules[self.current_rule_index]
            self.current_feature_index = 0
            print(f"Displaying question for rule: {self.current_question['current animal group']}")

            # Check if the current rule has 'required features'
            if "required features" in self.current_question:
                self.ask_feature_question()
            elif "end classification" in self.current_question:
                # Directly end classification if this is a terminal group
                self.end_classification(self.current_question["current animal group"])
            else:
                print(f"Error: No 'required features' or 'end classification' in rule for {self.current_question['current animal group']}.")
        else:
            print("No valid rule found. Ending classification with 'Unknown classification'.")
            self.end_classification("Unknown classification")

    def ask_feature_question(self):
        feature_name = self.current_question["required features"][self.current_feature_index]
        question_text = self.get_question_text(feature_name)
        print(f"Asking question: {question_text} (Feature: {feature_name})")
        self.question_label.config(text=question_text)

    def get_question_text(self, feature_name):
        for group in self.knowledge_base:
            for feature in group["features"]:
                if feature["name"] == feature_name:
                    print(f"Question text for feature '{feature_name}' found: {feature['question']}")
                    return feature.get("question", "No question available.")
        print(f"No question text found for feature '{feature_name}'.")
        return "No question available."

    def answer(self, user_input):
        feature_name = self.current_question["required features"][self.current_feature_index]
        self.answers[feature_name] = (user_input == "Yes")
        print(f"Answer received for feature '{feature_name}': {self.answers[feature_name]}")
        self.current_feature_index += 1

        if self.current_feature_index < 2:
            self.ask_feature_question()
        elif self.current_feature_index == 2:
            yes_count = sum(self.answers.get(feature, False) for feature in self.current_question["required features"][:2])
            print(f"First two features yes count: {yes_count}")
            if yes_count == 2:
                self.check_subcategories(self.current_question["new direction"])
            elif yes_count == 1:
                self.ask_feature_question()  # Ask the third question
            else:
                self.go_to_next_rule(self.current_question["else"])
        else:
            if self.answers[feature_name]:  # Third question is "Yes"
                self.check_subcategories(self.current_question["new direction"])
            else:  # Third question is "No"
                self.go_to_next_rule(self.current_question["else"])

    def check_subcategories(self, group):
        print(f"Checking subcategories for group: {group}")
        subcategory_rule_index = next(
            (index for index, rule in enumerate(self.rules) if rule["current animal group"] == group),
            None
        )
        if subcategory_rule_index is not None:
            print(f"Subcategories found. Transitioning to rule: {group}")
            self.current_rule_index = subcategory_rule_index
            self.display_next_question()
        else:
            print(f"No subcategories found. Ending classification for group: {group}")
            self.end_classification(group)

    def go_to_next_rule(self, next_group):
        print(f"Moving to next rule: {next_group}")
        self.current_rule_index = next(
            (index for index, rule in enumerate(self.rules) if rule["current animal group"] == next_group),
            None
        )
        self.display_next_question()

    def end_classification(self, classification_group):
        print(f"Ending classification. Group: {classification_group}")
        for rule in self.rules:
            if rule["current animal group"] == classification_group and "end classification" in rule:
                print(f"Final classification message: {rule['end classification']}")
                self.question_label.config(text=rule["end classification"])
                break
        self.yes_button.pack_forget()
        self.no_button.pack_forget()


# Initialize the app
root = tk.Tk()
app = KnowledgeBaseApp(root, knowledge_base, rules)
root.mainloop()
