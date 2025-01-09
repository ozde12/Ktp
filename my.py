from tkinter import Button, Label, Toplevel
from PIL import Image, ImageTk
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
                if animal == group_name:
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
                
    def end_classification(self, classification_group):
        print(f"Ending classification. Group: {classification_group}")
        for rule in self.rules:
            if rule["current animal group"] == classification_group and "end classification" in rule:
                end_message = rule["end classification"]
                parts = end_message.split("\n")
                secondary_message = parts[1]
                group_name = secondary_message.split("→")[-1].strip()
                # self.question_label.config(text=rule["end classification"])
                if group_name in self.animal_media[0]:
                    self.display_animal_images(group_name, end_message)
                break
        self.yes_button.pack_forget()
        self.no_button.pack_forget()


# Initialize the app
root = tk.Tk()
app = KnowledgeBaseApp(root, knowledge_base, rules)
root.mainloop()
