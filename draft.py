import tkinter as tk
import json

# Load the JSON data
with open('knowledge_base.json', 'r') as file:
    knowledge_data = json.load(file)

# The JSON structure is expected to have two keys which are Knowledge base and rules
knowledge_base = knowledge_data["Knowledge base"]
rules = knowledge_data["Rules"]

class KnowledgeBaseApp:
    """
    parameters:
    root: the main Tkinter window
    knowledge_base: it is loaded from the JSON 
    rules: specifies the flow of questions and the classification logic

    attributes:
    current_question: stores the current rule being processed
    current_feature_indec: tracks the current feature/question within a rule
    answer: is the dictionary to store user answers for features
    """
    def __init__(self, root, knowledge_base, rules):
        self.root = root
        self.knowledge_base = knowledge_base
        self.rules = rules
        self.current_question = None
        self.current_feature_index = 0  # Track which feature within the rule is being asked
        self.answers = {}  # Store user answers
        self.setup_gui()

    def setup_gui(self):
        # Main frame setup
        self.main_frame = tk.Frame(self.root, bg='#A5D6A7')  # Light green background
        self.main_frame.pack(fill="both", expand=True)

        # Welcome Label
        self.welcome_label = tk.Label(
            self.main_frame,
            text="Welcome to the Animal Classification System!",
            bg='#A5D6A7',
            fg='black',
            font=("Arial", 40, "bold"),
            wraplength=1100
        )
        self.welcome_label.place(relx=0.5, rely=0.4, anchor="center")

        # Start Button
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

        # Question label (initially hidden)
        self.question_label = tk.Label(
            self.main_frame,
            text="",
            bg='#A5D6A7',  # Light green background
            fg='black',  # Black text
            font=("Arial", 40, "bold"),
            wraplength=1100
        )
        
        # Frame for buttons to align them horizontally (initially hidden)
        self.button_frame = tk.Frame(self.main_frame, bg='#A5D6A7')

        # Yes button
        self.yes_button = tk.Button(
            self.button_frame,
            text="Yes",
            command=lambda: self.answer("Yes"),
            fg="black",  # Black text
            font=("Arial", 17),
            relief="solid",  # Solid line around the button
            padx=30,  # Padding for a larger clickable area
            pady=15
        )

        # No button
        self.no_button = tk.Button(
            self.button_frame,
            text="No",
            command=lambda: self.answer("No"),
            fg="black",  # Black text
            font=("Arial", 17),
            relief="solid",  # Solid line around the button
            padx=30,
            pady=15
        )

    # Start classification by showing the first question
    def start(self):
        # Hide welcome message and start button
        self.welcome_label.place_forget()
        self.start_button.place_forget()

        # Show question label and buttons
        self.question_label.place(relx=0.5, rely=0.4, anchor="center")
        self.button_frame.place(relx=0.5, rely=0.6, anchor="center")
        self.yes_button.pack(side="left", padx=40)
        self.no_button.pack(side="right", padx=40)

        self.display_next_question("1 and 2")  # Starting with the first set of questions

    """
    Displays the next question. 
    It looks for a rule with a matching "question number".
    If it finds the matching question numbers, it then initializes "current_question" and starts asking feature-related questions using ask_feature_question()
    """
    def display_next_question(self, question_number):
        for rule in self.rules:
            if rule["question number"] == question_number:
                self.current_question = rule
                self.current_feature_index = 0  # Reset feature index for the new rule
                self.ask_feature_question()
                return
        self.end_classification("No matching rule found.")

    # retrievs and displays a question for the current feature using get_question_text()
    def ask_feature_question(self):
        if self.current_feature_index < len(self.current_question["features"]):
            feature_name = self.current_question["features"][self.current_feature_index]
            question_text = self.get_question_text(feature_name)
            self.question_label.config(text=question_text)
        else:
            # All features in the rule have been answered; determine the next step
            self.determine_next_step()

    # searches the knowledge_base for  a matching feature name and returns the associated question text. If not found returns "Unknown question"
    def get_question_text(self, feature_name):
        for group in self.knowledge_base:
            for feature in group["features"]:
                if feature["name"] == feature_name:
                    return feature["question"]
        return "Unknown question"

    # records the user's answer as True for Yes annd No for False in the answers dictionary
    # Moves to the next feature or determines the next step if all features are answered
    def answer(self, user_input):
        feature_name = self.current_question["features"][self.current_feature_index]
        self.answers[feature_name] = (user_input == "Yes")  # Store True/False for the feature
        self.current_feature_index += 1  # Move to the next feature in the rule

        # Ask the next feature question, or move to the next step if all features are answered
        if self.current_feature_index < len(self.current_question["features"]):
            self.ask_feature_question()
        else:
            self.determine_next_step()

    """
    The logic for progressing based on the user's answers:
    For single-feature rules: Use true or false keys in the rule.
    For multi-feature rules: Checks if all features are True, all are False, or mixed.
    Uses keys like bothTrue, bothFalse or oneTrue
    Then checks if the next step is a classification (an "animal group") or another rule.
    """
    def determine_next_step(self):
        # Determine the next step based on answers to features
        current_rule = self.current_question
        features = current_rule["features"]

        if len(features) == 1:  # Single feature question
            next_step = current_rule["true"] if self.answers[features[0]] else current_rule["false"]
        else:  # Multiple features
            all_true = all(self.answers.get(feature, False) for feature in features)
            all_false = all(not self.answers.get(feature, False) for feature in features)

            if all_true:
                next_step = current_rule.get("bothTrue")
            elif all_false:
                next_step = current_rule.get("bothFalse")
            else:
                next_step = current_rule.get("oneTrue")

        if next_step in [group["animal group"] for group in self.knowledge_base]:  # Classification found
            self.end_classification(next_step)
        else:
            self.display_next_question(next_step)

    # displays the final classification result on the GUI
    # removes the "Yes" and "No" buttons, ending the interaction
    def end_classification(self, classification):
        self.question_label.config(text=f"The animal is classified as: {classification}")
        self.yes_button.pack_forget()
        self.no_button.pack_forget()

# Initialize the app
root = tk.Tk()
app = KnowledgeBaseApp(root, knowledge_base, rules)
root.mainloop()
