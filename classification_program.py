from tkinter import Button, Label, Toplevel
from PIL import Image, ImageTk
import tkinter as tk
import json


class KnowledgeBaseApp:
    def __init__(self, root, knowledge_base, rules, dictionary, animal_media, instructions):
        # Initializing the app with necessary parameters
        self.root = root
        self.knowledge_base = knowledge_base
        self.rules = rules
        self.dictionary = dictionary
        self.animal_media = animal_media  # Store animal media
        self.instructions = instructions
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
            wraplength=1200
        )
        self.welcome_label.place(relx=0.5, rely=0.4, anchor="center")

        # Instructions overview label (under the welcome message)
        self.instructions_label = tk.Label(
            self.main_frame,
            text="(Click on the question mark button for detailed instructions.)",
            bg='#A5D6A7',
            fg='#555555',
            font=("Arial", 18),
            wraplength=1100
        )
        self.instructions_label.place(relx=0.5, rely=0.465, anchor="center")

        def on_enter(event):
            event.widget['background'] = "#CCCCCC"

        def on_leave(event):
            event.widget['background'] = "white"

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
        self.start_button.bind("<Enter>", on_enter)
        self.start_button.bind("<Leave>", on_leave)

        # Frame to allign tree, dictionary and question mark buttons
        self.top_button_frame = tk.Frame(self.root, bg='#A5D6A7')
        self.top_button_frame.place(relx=0.98, rely=0.05, anchor="ne")

        # Tree button
        self.tree_button = tk.Button(
            self.top_button_frame,
            text="Show Classification Tree",
            command=self.show_classification_tree,
            fg="black",
            font=("Arial", 15),
            relief="raised",
            padx=10,
            pady=5
        )
        self.tree_button.pack(side="left", padx=1.5)
        self.tree_button.bind("<Enter>", on_enter)
        self.tree_button.bind("<Leave>", on_leave)

        # Dictionary button (always visible)
        self.dictionary_button = tk.Button(
            self.top_button_frame,
            text="Open Dictionary",
            command=self.open_dictionary,
            fg="black",
            font=("Arial", 15),
            relief="raised",
            padx=10,
            pady=5
        )
        self.dictionary_button.pack(side="left", padx=1.5)
        self.dictionary_button.bind("<Enter>", on_enter)
        self.dictionary_button.bind("<Leave>", on_leave)

        # Question Mark button (for Instructions)
        self.question_mark_button = tk.Button(
            self.top_button_frame,
            text="?",
            command=self.show_instructions,
            fg="black",
            font=("Arial", 15),
            relief="raised",
            padx=10,
            pady=5
        )
        self.question_mark_button.pack(side="left", padx=1.5)
        self.question_mark_button.bind("<Enter>", on_enter)
        self.question_mark_button.bind("<Leave>", on_leave)

        # Question label (initially hidden, will be shown when asking a question)
        self.question_label = tk.Label(
            self.main_frame,
            text="",
            bg='#A5D6A7',  # Light green background
            fg='black',  # Black text
            font=("Arial", 40, "bold"),
            wraplength=1100
        )

        # Frame for yes/no buttons to align them horizontally (initially hidden)
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
        self.yes_button.bind("<Enter>", on_enter)
        self.yes_button.bind("<Leave>", on_leave)

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
        self.no_button.bind("<Enter>", on_enter)
        self.no_button.bind("<Leave>", on_leave)

        # Animal group label (hidden at the start)
        self.animal_group_label = tk.Label(
            self.main_frame,
            text="Current Animal Group: None",
            bg='#A5D6A7',
            fg='black',
            font=("Arial", 14),
            anchor="w"
        )

        # This label will show up later during the classification and update
        self.animal_group_label.place(relx=0.01, rely=0.05)  # Position at the top left
        self.animal_group_label.place_forget()  # Initially hide it


    def show_instructions(self):
        instructions_window = tk.Toplevel(self.root)
        instructions_window.title("Instructions")
        instructions_window.geometry(f"700x600+{self.root.winfo_x() + 800}+{self.root.winfo_y() + 150}")

        scrollable_frame = tk.Frame(instructions_window)
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

        for i, instruction in enumerate(self.instructions):
            if i == 0:
                instruction_label = tk.Label(frame_content, text=instruction, font=("Arial", 16, "bold"), wraplength=600, anchor="w", justify="left")
            else:
                instruction_label = tk.Label(frame_content, text=instruction, font=("Arial", 14), wraplength=600, anchor="w", justify="left")
            instruction_label.pack(pady=5)


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

        # Start the main loop
        self.root.mainloop()


    def open_dictionary(self):
        dictionary_window = tk.Toplevel(self.root)
        dictionary_window.title("Dictionary")
        dictionary_window.geometry(f"700x600+{self.root.winfo_x() + 800}+{self.root.winfo_y() + 150}")

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


    def show_classification_tree(self):
        img_path = "Images\\animal tree.png"
        img = Image.open(img_path)
        img = img.resize((600, 600))
        
        img_window = Toplevel(self.root)
        img_window.title("Classification Tree")
        img_window.geometry("600x600+10+100")
        
        tk_img = ImageTk.PhotoImage(img)
        img_label = Label(img_window, image=tk_img)
        img_label.image = tk_img
        img_label.pack()


    def process_rule(self, rule):
        #1
        print("MOVING ON TO THE PROCESS RULE FUNCTION")
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
            print(current_animal_group)
            self.animal_group_label.place(relx=0.01, rely=0.05)  # Show the animal group label
            
            # Initialize initial features for the current animal group (taking the first two features)
            self.initial_features = [feature["name"] for feature in self.current_question["features"][:2]]
            self.initial_feature_index = 0  # Start asking the first feature

            # Ask the initial feature questions
            self.ask_initial_features(self.rule_from_rules)  # Pass the correct rule
            #self.ask_initial_features()
        else:
            print(f"No rule found for animal group: {current_animal_group}")


    def get_animal_group_data(self, group_name):
        #2
        print("MOVING ON TO THE GET ANIMAL GROUP DATA FUNCTION")
        # Search for the animal group data in the knowledge base
        print(f"Searching for data for animal group: {group_name}")
        for group in self.knowledge_base:
            if group["animal group"] == group_name:
                return group
        print(f"No data found for animal group: {group_name}")
        return None


    def ask_initial_features(self, current_animal_group):
        #3
        print("MOVING ON TO THE ASK INITIAL FEATURES FUNCTION")
        # Check if there are still features left to ask
        if self.initial_feature_index < len(self.initial_features):
            feature_name = self.initial_features[self.initial_feature_index]

            question_number = self.initial_feature_index + 1    
            print(f"Asking about feature number {question_number}: {feature_name}")
            question_text = self.get_question_text(feature_name)
            self.question_label.config(text=question_text)
        else:
            # After the first two questions, compare the stored features with required features
            print("Initial questions complete, comparing features with rule...")
            self.compare_features_with_rule(current_animal_group)
            #self.compare_features_with_rule()


    def get_question_text(self, feature_name):
        #4
        print("MOVING ON TO THE GET QUESTION TEXT FUNCTION")
        # Search for the feature and return the corresponding question
        print(f"Getting question for feature: {feature_name}")
        for index, feature in enumerate(self.current_question["features"], start = 1):
            if feature["name"] == feature_name:
                print(f"Feature number: {index}, Feature name: {feature_name}")
                return feature["question"], index
        print(f"No question found for feature: {feature_name}")
        return ""


    def answer(self, user_input, feature_number=None):
        print("MOVING ON TO THE ANSWER FUNCTION")
        
        # If feature_number is provided, use it; otherwise, fall back to existing logic
        
        if feature_number is None:
            feature_name = self.initial_features[self.initial_feature_index]
            question_text, feature_number = self.get_question_text(feature_number)
            print(f"Feature determined from get_question_text. Feature name: {feature_name}, Feature number: {feature_number}")
        else:
            feature_name = self.current_question["features"][feature_number - 1]["name"]
            question_text = self.get_question_text(feature_name)[0]
            print(f"Using provided feature number: {feature_number}. Feature name: {feature_name}")

        # Process user input (logic to be added based on your specific requirements)
        print(f"Processing user input for Feature: {feature_name}, Feature Number: {feature_number}")

        """if not self.asking_third_question:  # If we're not in the third question phase
                feature_name = self.initial_features[self.initial_feature_index]
                feature_number = self.initial_feature_index + 1  # Feature number based on the index
                print(f"Feature is from initial features. Feature name: {feature_name}, Feature number: {feature_number}")
            else:  # If it's the third question phase
                feature_name = self.current_question["features"][2]["name"]
                feature_number = 3  # Explicitly set for third question
                print(f"Feature is from third question phase. Feature name: {feature_name}, Feature number: {feature_number}")
        else:
            print(f"Using passed feature number: {feature_number}")"""

        # Store the user's answer for the feature
        print(f"Storing answer for feature number {feature_number}: {feature_name}")
        print(f"User answered {user_input} for feature: {feature_name}")
    
        # Store the answer
        self.answers[feature_name] = (user_input == "Yes")
        if user_input == "Yes":
            self.stored_features.append(feature_name)
    
        # Debug print to show stored features and answers
        print(f"Stored features: {self.stored_features}")
        print(f"Answers so far: {self.answers}")

        # Move to the next feature or process the rule
        if not self.asking_third_question:  # If not in third question phase
            self.initial_feature_index += 1
            print(f"Initial feature index after increment: {self.initial_feature_index}")
            if self.initial_feature_index < len(self.initial_features):
                self.ask_initial_features(self.rule_from_rules["current animal group"])
            else:
                print("All initial questions answered. Comparing features with rule...")
                self.compare_features_with_rule(self.rule_from_rules)
                #self.compare_features_with_rule()
        else:  # If in third question phase
            print("After third question, comparing features with rule again...")
            self.compare_features_with_rule(self.rule_from_rules)
            #self.compare_features_with_rule()


    # last
    def compare_features_with_rule(self, current_rule):
        print("MOVING ON TO THE COMPARE FEATURES WITH RULE FUNCTION")   
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
        print("MOVING ON TO THE ASK THIRD QUESTION FUNCTION")
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
        print("MOVING ON TO THE HANDLE THIRD ANSWER FUNCTION")
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
        print("MOVING ON TO THE DISPLAY NEXT QUESTION FUNCTION")    
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
            message_frame.place(relx=0.5, rely=0.45, anchor="center")
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

            examples_message = tk.Label(
                message_frame,
                text=f"Some examples of {group_name} (hover over them):",
                bg='#A5D6A7',
                fg='black',
                font=("Arial", 20),
                wraplength=1100
            )
            examples_message.pack(pady=(100, 0))
            
            message_frame.update_idletasks()
            message_frame_height = message_frame.winfo_height()

            images_frame = tk.Frame(self.main_frame, bg="#A5D6A7", width=800, height=400)
            images_frame.place(relx=0.5, rely=0.5 + (message_frame_height / self.main_frame.winfo_height()) - 0.2, anchor="n")

            x_pos, y_pos = 50, 0
            for animal in media["Images"]:
                img = Image.open(animal["File"]).resize((200, 200))
                photo = ImageTk.PhotoImage(img)
                img_label = Label(images_frame, image=photo, bg="#A5D6A7")
                img_label.image = photo
                img_label.place(x=x_pos, y=y_pos)

                def on_enter(event, name=animal["Name"], fact=animal["Fact"]):
                    hover_label = Label(images_frame, text=f"{name}: {fact}", bg="#FFF", fg="black", font=("Arial", 12))
                    hover_label.place(x=min(event.x_root - images_frame.winfo_rootx() + 10, images_frame.winfo_width() - hover_label.winfo_reqwidth() - 10),
                                      y=min(event.y_root - images_frame.winfo_rooty() + 10, images_frame.winfo_height() - hover_label.winfo_reqheight() - 10))
                    event.widget.hover_label = hover_label

                def on_leave(event):
                    if hasattr(event.widget, "hover_label"):
                        event.widget.hover_label.destroy()
                        del event.widget.hover_label

                img_label.bind("<Enter>", on_enter)
                img_label.bind("<Leave>", on_leave)

                x_pos += 220


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


def main() -> None:
    with open('knowledge_base.json', 'r') as file:
        knowledge_data = json.load(file)

    knowledge_base = knowledge_data["Knowledge base"]
    rules = knowledge_data["Rules"]
    dictionary_data = knowledge_data["Dictionary"]
    animal_media = knowledge_data.get("Animal media", {})
    instructions = knowledge_data.get("Instructions", "")

    root = tk.Tk()
    KnowledgeBaseApp(root, knowledge_base, rules, dictionary_data, animal_media, instructions)

    # Ensuring the Tkinter event loop is properly handled in macOS
    root.mainloop()


if __name__ == "__main__":
    main()
