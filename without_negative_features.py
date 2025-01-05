from tkinter import Toplevel, Canvas, Label
from PIL import Image, ImageTk
import tkinter as tk
import json

# Load the JSON data (this file should contain the knowledge base and rules)
with open('without_negative_features.json', 'r') as file:
    knowledge_data = json.load(file)

# The JSON structure is expected to have additional media information under "Animal media"
knowledge_base = knowledge_data["Knowledge base"]
rules = knowledge_data["Rules"]
dictionary_data = knowledge_data["Dictionary"]
animal_media = knowledge_data.get("Animal media", {})  # Optional "Animal media" key

class KnowledgeBaseApp:
    def __init__(self, root, knowledge_base, rules, dictionary, animal_media):
        # Initializing the app with necessary parameters
        self.root = root
        self.knowledge_base = knowledge_base
        self.rules = rules
        self.dictionary = dictionary
        self.animal_media = animal_media  # Store animal media
        self.current_question = None
        self.current_feature_index = 0  # Track which feature within the rule is being asked
        self.answers = {}  # Store user answers
        self.stored_features = []  # Store features where the answer is 'Yes'
        self.initial_features = []  # Initial feature questions (we'll populate this later)
        self.initial_feature_index = 0  # Track progress in answering initial questions
        self.initial_phase_complete = False  # Track if initial questions are completed
        self.asking_third_question = False  # Flag for checking third question
        self.third_question_answered = False  # Ensure third question is only asked once
        self.setup_gui()

    def setup_gui(self):
        # Setting up the main frame for the UI
        self.main_frame = tk.Frame(self.root, bg='#A5D6A7')  # Light green background
        self.main_frame.pack(fill="both", expand=True)

        # Set up the root window
        self.root.geometry("1200x800")  # Set initial window size (adjustable for macOS screen)
        self.root.title("Animal Classification System")  # Window title

        # Welcome Label (this will be shown initially)
        self.welcome_label = tk.Label(
            self.main_frame,
            text="Welcome to the Animal Classification System!",
            bg='#A5D6A7',
            fg='black',
            font=("Arial", 40, "bold"),
            wraplength=1100
        )
        self.welcome_label.place(relx=0.5, rely=0.4, anchor="center")

        # Start Button to start the classification process
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

        # Dictionary button (always visible)
        self.dictionary_button = tk.Button(
            self.root,  # Attach it directly to the root window
            text="Open Dictionary",
            command=self.open_dictionary,
            fg="black",
            font=("Arial", 15),
            relief="solid",
            padx=10,
            pady=5
        )
        self.dictionary_button.place(relx=0.9, rely=0.05, anchor="ne")  # Fixed top-right corner

        # Question label (initially hidden, will be shown when asking a question)
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

        # Animal group label (hidden at the start)
        self.animal_group_label = tk.Label(
            self.main_frame,
            text="Current Animal Group: None",
            bg='#A5D6A7',
            fg='black',
            font=("Arial", 12),
            anchor="w"
        )

        # This label will show up later during the classification and update
        self.animal_group_label.place(relx=0.01, rely=0.05)  # Position at the top left
        self.animal_group_label.place_forget()  # Initially hide it

    def start(self):
        # Hide welcome message and start button when the user clicks "Start"
        print("Starting the application...")
        self.welcome_label.place_forget()
        self.start_button.place_forget()

        # Show question label and buttons to start asking questions
        self.question_label.place(relx=0.5, rely=0.4, anchor="center")
        self.button_frame.place(relx=0.5, rely=0.6, anchor="center")
        self.yes_button.pack(side="left", padx=40)
        self.no_button.pack(side="right", padx=40)

        # Start with the first rule
        print("Processing the first rule...")
        self.process_rule(self.rules[0])

    def open_dictionary(self):
        dictionary_window = tk.Toplevel(self.root)
        dictionary_window.title("Dictionary")
        dictionary_window.geometry("600x600")

        # Create a scrollable frame
        scrollable_frame = tk.Frame(dictionary_window)
        scrollable_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(scrollable_frame)
        scrollbar = tk.Scrollbar(scrollable_frame, orient="vertical", command=canvas.yview)
        frame_content = tk.Frame(canvas)

        frame_content.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=frame_content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add dictionary terms and definitions
        for entry in self.dictionary:
            term_label = tk.Label(frame_content, text=f"{entry['Term']}", font=("Arial", 14, "bold"), anchor="w")
            definition_label = tk.Label(frame_content, text=f"{entry['Definition']}", font=("Arial", 12), wraplength=550, anchor="w", justify="left")
            term_label.pack(fill="x", pady=5)
            definition_label.pack(fill="x", pady=(0, 10))

    def process_rule(self, rule):
        # Find the rule for the current animal group from the Rules section
        current_animal_group = rule["current animal group"]
        print(f"Processing rule for animal group: {current_animal_group}")
        
        # Get the correct rule from the 'Rules' section based on the 'current animal group'
        self.rule_from_rules = next((r for r in self.rules if r["current animal group"] == current_animal_group), None)

        if self.rule_from_rules:
            self.current_question = self.get_animal_group_data(current_animal_group)
            
            # Update the animal group label at the top left
            print(f"Setting animal group label to: {current_animal_group}")
            self.animal_group_label.config(text=f"Current Animal Group: {current_animal_group}")
            self.animal_group_label.place(relx=0.01, rely=0.05)  # Show the animal group label
            
            # Initialize initial features for the current animal group (taking the first two features)
            self.initial_features = [feature["name"] for feature in self.current_question["features"][:2]]
            self.initial_feature_index = 0  # Start asking the first feature

            # Ask the initial feature questions
            self.ask_initial_features(self.rule_from_rules)  # Pass the correct rule
        else:
            print(f"No rule found for animal group: {current_animal_group}")

    def get_animal_group_data(self, group_name):
        # Search for the animal group data in the knowledge base
        print(f"Searching for data for animal group: {group_name}")
        for group in self.knowledge_base:
            if group["animal group"] == group_name:
                return group
        print(f"No data found for animal group: {group_name}")
        return None

    def ask_initial_features(self, current_animal_group):
        # Check if there are still features left to ask
        if self.initial_feature_index < len(self.initial_features):
            feature_name = self.initial_features[self.initial_feature_index]
            print(f"Asking about feature: {feature_name}")
            question_text = self.get_question_text(feature_name)
            self.question_label.config(text=question_text)
        else:
            # After the first two questions, compare the stored features with required features
            print("Initial questions complete, comparing features with rule...")
            self.compare_features_with_rule(current_animal_group)

    def get_question_text(self, feature_name):
        # Search for the feature and return the corresponding question
        print(f"Getting question for feature: {feature_name}")
        for feature in self.current_question["features"]:
            if feature["name"] == feature_name:
                return feature["question"]
        print(f"No question found for feature: {feature_name}")
        return ""

    def answer(self, user_input):
        # Store the user's answer for the feature
        if not self.asking_third_question:  # If we're not in the third question phase
            feature_name = self.initial_features[self.initial_feature_index]
        else:  # If it's the third question phase
            feature_name = self.current_question["features"][2]["name"]
        
        print(f"User answered {user_input} for feature: {feature_name}")
        self.answers[feature_name] = (user_input == "Yes")
        if user_input == "Yes":
            self.stored_features.append(feature_name)

        # Move to the next feature or process the rule
        if not self.asking_third_question:  # If not in third question phase
            self.initial_feature_index += 1
            if self.initial_feature_index < len(self.initial_features):
                self.ask_initial_features(self.rule_from_rules["current animal group"])
            else:
                print("All initial questions answered. Comparing features with rule...")
                self.compare_features_with_rule(self.rule_from_rules)
        else:  # If in third question phase
            print("After third question, comparing features with rule again...")
            self.compare_features_with_rule(self.rule_from_rules)

    def compare_features_with_rule(self, current_rule):
        # Ensure the rule contains the "required features" key
        print(f"Current rule: {current_rule}")  # Debugging print
        
        # Safely access 'required features' from the current rule
        required_features = current_rule.get("required features")
        print(f"Required features: {required_features}")
        
        if not required_features:
            print(f"Error: Rule for {current_rule.get('current animal group', 'Unknown group')} does not contain 'required features'. Skipping this rule.")
            return  # Skip the rule if it doesn't have required features
        
        print("Comparing stored features with required features...")

        # Count how many required features the user has answered "Yes" to
        feature_matches = sum(1 for feature in required_features if feature in self.stored_features)
        
        print(f"Feature matches: {feature_matches} out of {len(required_features)} required features.")
        
        if feature_matches >= 2:
            # If 2 or more features match, proceed to the new direction
            print(f"Feature matches sufficient. Moving to new direction: {current_rule['new direction']}")
            self.display_next_question(current_rule["new direction"])
        elif not self.asking_third_question:
            # If feature matches are insufficient, and the third question hasn't been asked yet
            print("Feature matches insufficient. Asking the third question...")
            self.ask_third_question(current_rule)  # Ask the third question
            self.asking_third_question = True  # Mark that the third question has been asked
        else:
            # If feature matches are insufficient and the third question has already been asked
            print("Feature matches insufficient. Moving to the 'else' of the current rule...")
            self.display_next_question(current_rule["else"])

    def ask_third_question(self, rule):
        # Only ask the third question once (if the flag is False)
        if not self.asking_third_question:
            self.asking_third_question = True  # Mark as asked
            feature_name = self.current_question["features"][2]["name"]
            print(f"Asking third question for feature: {feature_name}")
            question_text = self.get_question_text(feature_name)
            self.question_label.config(text=question_text)
            self.asking_third_question = True  # Flag to indicate third question is being asked
        else:
            # If the third question was already asked, directly move to the "else" section
            print("Third question has already been asked. Moving to the next rule or direction...")
            self.compare_features_with_rule(rule)

    def handle_third_answer(self, user_input):
        # Store the answer to the third question
        feature_name = self.current_question["features"][2]["name"]
        print(f"User answered {user_input} for third question on feature: {feature_name}")
        self.answers[feature_name] = (user_input == "Yes")
        if user_input == "Yes":
            self.stored_features.append(feature_name)
        
        # After the third question, check the features again
        print("After third question, comparing features with rule again...")
        self.compare_features_with_rule(self.rule_from_rules)

    def display_next_question(self, group_name):
        # Check if the group_name is a classification endpoint
        print(f"Displaying next question for group: {group_name}")
        if group_name.startswith("classification"):
            # Find the rule with the "end classification" message
            rule = next((rule for rule in self.rules if rule["current animal group"] == group_name), None)
            if rule and "end classification" in rule:
                self.end_classification(rule["end classification"])
        else:
            # Find the next rule to follow
            next_rule = next((rule for rule in self.rules if rule["current animal group"] == group_name), None)
            if next_rule:
                self.process_rule(next_rule)

    def display_animal_images(self, group_name, classification_message):
        if group_name in self.animal_media[0]:
            media = self.animal_media[0][group_name]
            message_frame = tk.Frame(self.main_frame, bg='#A5D6A7')
            message_frame.place(relx=0.5, rely=0.5, anchor="center")
            parts = classification_message.split("\n")
            main_message = parts[0]
            secondary_message = parts[1] if len(parts) > 1 else ""
            
            main_label = tk.Label(
                message_frame,
                text=main_message,
                bg='#A5D6A7',
                fg='black',
                font=("Arial", 40, "bold"),
                wraplength=1100
            )
            main_label.pack()

            secondary_label = tk.Label(
                message_frame,
                text=secondary_message,
                bg='#A5D6A7',
                fg='#555555',
                font=("Arial", 30),
                wraplength=1100
            )
            secondary_label.pack(pady=(10, 0))
            
            message_frame.update_idletasks()
            message_frame_height = message_frame.winfo_height()

            images_frame = tk.Frame(self.main_frame, bg="#A5D6A7", width=800, height=400)
            images_frame.place(relx=0.5, rely=0.5 + (message_frame_height / self.main_frame.winfo_height()), anchor="n")

            x_pos, y_pos = 50, 0
            for animal in media["Images"]:
                img = Image.open(animal["File"]).resize((200, 200))
                photo = ImageTk.PhotoImage(img)
                img_label = Label(images_frame, image=photo, bg="#A5D6A7")
                img_label.image = photo
                img_label.place(x=x_pos, y=y_pos)

                def on_enter(event, name=animal["Name"], fact=animal["Fact"]):
                    hover_label = Label(images_frame, text=f"{name}: {fact}", bg="#FFF", fg="black", font=("Arial", 12))
                    hover_label.place(x=event.x_root - images_frame.winfo_rootx() + 10,
                                    y=event.y_root - images_frame.winfo_rooty() + 10)
                    event.widget.hover_label = hover_label

                def on_leave(event):
                    if hasattr(event.widget, "hover_label"):
                        event.widget.hover_label.destroy()
                        del event.widget.hover_label

                img_label.bind("<Enter>", on_enter)
                img_label.bind("<Leave>", on_leave)

                x_pos += 250
                if x_pos > 600:
                    x_pos = 50
                    y_pos += 250

    def end_classification(self, classification_message):
        # Clear the main frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Separate the main and secondary parts of the message
        parts = classification_message.split("\n")
        main_message = parts[0]
        secondary_message = parts[1] if len(parts) > 1 else ""
        group_name = secondary_message.split("→")[-1].strip()  # Extract group name

        if group_name in self.animal_media[0]:
            group_data = self.animal_media[0][group_name]
            self.display_animal_images(group_name, classification_message)

# Initialize the app
root = tk.Tk()
app = KnowledgeBaseApp(root, knowledge_base, rules, dictionary_data, animal_media)

# Ensuring the Tkinter event loop is properly handled in macOS
root.mainloop()
