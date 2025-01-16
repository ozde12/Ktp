import tkinter as tk
from tkinter import Label, Toplevel
import json

from PIL import Image, ImageTk


class KnowledgeBaseApp:
    def __init__(self, root, knowledge_base, rules, dictionary, animal_media, instructions) -> None:
        self.root = root
        self.knowledge_base = knowledge_base
        self.rules = rules
        self.dictionary = dictionary
        self.animal_media = animal_media
        self.instructions = instructions
        self.current_rule_index = None
        self.current_feature_index = 0
        self.answers = {}
        self.current_question = None
        self.setup_gui()

    def restart_program(self):
        # Restarts the entire program
        self.root.quit()
        self.root.destroy()
        main()

    def exit_fullscreen(self, event=None) -> None:
        # Exit the full-screen mode when the ESC key is pressed
        self.root.wm_attributes("-fullscreen", False)
        
        window_width = 1000
        window_height = 600

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        self.root.geometry(f"{window_width}x{window_height}")
        self.root.update_idletasks()

        true_window_width = self.root.winfo_width()
        true_window_height = self.root.winfo_height()

        position_left = (screen_width // 2) - (true_window_width // 2)
        position_top = (screen_height // 2) - (true_window_height // 2)

        self.root.geometry(f"{true_window_width}x{true_window_height}+{position_left}+{position_top}")

    def on_enter_buttons(self, event) -> None:
        event.widget['background'] = "#CCCCCC"

    def on_leave_buttons(self, event) -> None:
        event.widget['background'] = "white"

    def setup_gui(self) -> None:
        self.main_frame = tk.Frame(self.root, bg='#A5D6A7')
        self.main_frame.pack(fill="both", expand=True)

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        self.root.geometry(f"{screen_width}x{screen_height}")
        self.root.bind("<Escape>", self.exit_fullscreen)
        self.root.title("Animal Classification System")

        self.welcome_label = tk.Label(
            self.main_frame,
            text="Welcome to the Animal Classification System!",
            bg='#A5D6A7',
            fg='black',
            font=("Arial", 40, "bold"),
            wraplength=1200
        )
        self.welcome_label.place(relx=0.5, rely=0.4, anchor="center")

        self.instructions_label = tk.Label(
            self.main_frame,
            text="(Click on the question mark button for detailed instructions.)",
            bg='#A5D6A7',
            fg='#555555',
            font=("Arial", 20),
            wraplength=1100
        )
        self.instructions_label.place(relx=0.5, rely=0.465, anchor="center")

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
        self.start_button.bind("<Enter>", self.on_enter_buttons)
        self.start_button.bind("<Leave>", self.on_leave_buttons)

        # Frame to allign tree, dictionary, restart, and question mark buttons
        self.top_button_frame = tk.Frame(self.root, bg='#A5D6A7')
        self.top_button_frame.place(relx=0.98, rely=0.05, anchor="ne")

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
        self.tree_button.bind("<Enter>", self.on_enter_buttons)
        self.tree_button.bind("<Leave>", self.on_leave_buttons)

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
        self.dictionary_button.bind("<Enter>", self.on_enter_buttons)
        self.dictionary_button.bind("<Leave>", self.on_leave_buttons)

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
        self.question_mark_button.pack(side="left", padx=(1.5, 20))
        self.question_mark_button.bind("<Enter>", self.on_enter_buttons)
        self.question_mark_button.bind("<Leave>", self.on_leave_buttons)

        self.restart_button = tk.Button(
            self.top_button_frame,
            text="Restart",
            command=self.restart_program,
            fg="black",
            font=("Arial", 15),
            relief="raised",
            padx=10,
            pady=5
        )
        self.restart_button.pack(side="left", padx=1.5)
        self.restart_button.bind("<Enter>", self.on_enter_buttons)
        self.restart_button.bind("<Leave>", self.on_leave_buttons)

        self.question_label = tk.Label(
            self.main_frame,
            text="",
            bg='#A5D6A7',
            fg='black',
            wraplength=1100
        )

        self.answer_button_frame = tk.Frame(self.main_frame, bg='#A5D6A7')

        self.yes_button = tk.Button(
            self.answer_button_frame,
            text="Yes",
            command=lambda: self.answer("Yes"),
            fg="black",
            font=("Arial", 17),
            relief="solid",
            padx=30,
            pady=15
        )
        self.yes_button.bind("<Enter>", self.on_enter_buttons)
        self.yes_button.bind("<Leave>", self.on_leave_buttons)

        self.no_button = tk.Button(
            self.answer_button_frame,
            text="No",
            command=lambda: self.answer("No"),
            fg="black",
            font=("Arial", 17),
            relief="solid",
            padx=30,
            pady=15
        )
        self.no_button.bind("<Enter>", self.on_enter_buttons)
        self.no_button.bind("<Leave>", self.on_leave_buttons)

        self.animal_group_label = tk.Label(
            self.main_frame,
            text="Current Animal Group: None",
            bg='#A5D6A7',
            fg='black',
            font=("Arial", 14),
            anchor="w"
        )

        self.animal_group_label.place(relx=0.01, rely=0.05)
        self.animal_group_label.place_forget()

    def show_instructions(self) -> None:
        instructions_window = tk.Toplevel(self.root)
        instructions_window.title("Instructions")
        instructions_window.geometry(f"700x600+{self.root.winfo_x()+680}+{self.root.winfo_y()+150}")

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

    def open_dictionary(self) -> None:
        dictionary_window = tk.Toplevel(self.root)
        dictionary_window.title("Dictionary")
        dictionary_window.geometry(f"700x600+{self.root.winfo_x()+680}+{self.root.winfo_y()+150}")

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

        for entry in self.dictionary:
            term_label = tk.Label(frame_content, text=f"{entry['Term']}", font=("Arial", 14, "bold"), anchor="w")
            definition_label = tk.Label(frame_content, text=f"{entry['Definition']}", font=("Arial", 12), wraplength=550, anchor="w", justify="left")
            term_label.pack(fill="x", pady=5)
            definition_label.pack(fill="x", pady=(0, 10))

    def show_classification_tree(self) -> None:
        img_path = "Images/animal tree.png"
        img = Image.open(img_path)
        img = img.resize((600, 600))
        
        img_window = Toplevel(self.root)
        img_window.title("Classification Tree")
        img_window.geometry("600x600+10+100")
        
        tk_img = ImageTk.PhotoImage(img)
        img_label = Label(img_window, image=tk_img)
        img_label.image = tk_img
        img_label.pack()

    def update_animal_group_label(self, label) -> None:
        vowels = ('a', 'e', 'i', 'o', 'u')

        if label.endswith('s'):
            label = label.rstrip('s')

        if label.startswith(vowels):
            self.animal_group_label.config(text=f"Your animal is an {label}")
        else:
            self.animal_group_label.config(text=f"Your animal is a {label}")

        self.animal_group_label.place(relx=0.01, rely=0.05)

    def start(self) -> None:
        self.start_button.place_forget()
        self.welcome_label.place_forget()
        self.instructions_label.place_forget()
        self.question_label.place(relx=0.5, rely=0.4, anchor="center")
        self.answer_button_frame.place(relx=0.5, rely=0.6, anchor="center")
        self.yes_button.pack(side="left", padx=40)
        self.no_button.pack(side="right", padx=40)
        self.current_rule_index = 0
        self.display_next_question()

    def display_next_question(self) -> None:
        if self.current_rule_index is not None and self.current_rule_index < len(self.rules):
            self.current_question = self.rules[self.current_rule_index]
            self.current_feature_index = 0
            # print(f"Displaying question for rule: {self.current_question['current animal group']}")

            if "required features" in self.current_question:
                self.ask_feature_question()
            elif "end classification" in self.current_question:
                # Directly end classification if this is a terminal group
                self.end_classification(self.current_question["current animal group"])
            else:
                print(f"Error: No 'required features' or 'end classification' in rule for {self.current_question['current animal group']}.")
        else:
            # print("No valid rule found. Ending classification with 'Unknown classification'.")
            self.end_classification("Unknown classification")

    def ask_feature_question(self) -> None:
        feature_name = self.current_question["required features"][self.current_feature_index]
        question_text = self.get_question_text(feature_name)
        # print(f"Asking question: {question_text} (Feature: {feature_name})")
        if len(question_text.split()) > 15:
            font_style = ("Arial", 33, "bold")
        else:
            font_style = ("Arial", 40, "bold")
        self.question_label.config(text=question_text, font=font_style)

    def get_question_text(self, feature_name) -> str:
        for group in self.knowledge_base:
            for feature in group["features"]:
                if feature["name"] == feature_name:
                    # print(f"Question text for feature '{feature_name}' found: {feature['question']}")
                    return feature.get("question", "No question available.")
        # print(f"No question text found for feature '{feature_name}'.")
        return "No question available."

    def answer(self, user_input) -> None:
        feature_name = self.current_question["required features"][self.current_feature_index]
        self.answers[feature_name] = (user_input == "Yes")
        # print(f"Answer received for feature '{feature_name}': {self.answers[feature_name]}")
        self.current_feature_index += 1

        if self.current_feature_index < 2:
            self.ask_feature_question()
        elif self.current_feature_index == 2:
            yes_count = sum(self.answers.get(feature, False) for feature in self.current_question["required features"][:2])
            # print(f"First two features yes count: {yes_count}")
            if yes_count == 2:
                self.update_animal_group_label(self.current_question['current animal group'])
                self.check_subcategories(self.current_question["new direction"])
            elif yes_count == 1:
                self.ask_feature_question()  # Ask the third question
            else:
                if self.current_question['current animal group'] == "vertebrates":
                    self.update_animal_group_label("invertebrates")
                self.go_to_next_rule(self.current_question["else"])
        else:
            if self.answers[feature_name]:  # Third question is "Yes"
                self.update_animal_group_label(self.current_question['current animal group'])
                self.check_subcategories(self.current_question["new direction"])
            else:  # Third question is "No"
                if self.current_question['current animal group'] == "vertebrates":
                    self.update_animal_group_label("invertebrate")
                self.go_to_next_rule(self.current_question["else"])

    def check_subcategories(self, group) -> None:
        # print(f"Checking subcategories for group: {group}")
        subcategory_rule_index = next(
            (index for index, rule in enumerate(self.rules) if rule["current animal group"] == group),
            None
        )
        if subcategory_rule_index is not None:
            # print(f"Subcategories found. Transitioning to rule: {group}")
            self.current_rule_index = subcategory_rule_index
            self.display_next_question()
        else:
            # print(f"No subcategories found. Ending classification for group: {group}")
            self.end_classification(group)

    def go_to_next_rule(self, next_group) -> None:
        # print(f"Moving to next rule: {next_group}")
        self.current_rule_index = next(
            (index for index, rule in enumerate(self.rules) if rule["current animal group"] == next_group),
            None
        )
        self.display_next_question()

    def display_animal_images(self, group_name, message_frame) -> None:
        for group in self.animal_media:
            if group_name in group:
                media = group[group_name]

                if not (group_name.endswith('s') or group_name.endswith('fish')):
                    group_name = f"{group_name}s"

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
                break

    def end_classification(self, classification_group) -> None:
        # print(f"Ending classification. Group: {classification_group}")
        rule_found = False

        for rule in self.rules:
            if rule["current animal group"] == classification_group and "end classification" in rule:
                rule_found = True
                self.animal_group_label.place_forget()
                self.yes_button.pack_forget()
                self.no_button.pack_forget()
                self.question_label.place_forget()

                end_message = rule["end classification"]
                main_message = end_message.split("\n")[0]
                secondary_message = end_message.split("\n")[1]
                group_name = " ".join(classification_group.split(" ")[1:])

                message_frame = tk.Frame(self.main_frame, bg='#A5D6A7')
                message_frame.place(relx=0.5, rely=0.45, anchor="center")

                if len(main_message.split()) <= 10:
                    main_label = tk.Label(
                        message_frame,
                        text=main_message,
                        bg='#A5D6A7',
                        fg='black',
                        font=("Arial", 40, "bold"),
                        wraplength=1200
                    )
                    main_label.pack()

                    secondary_label = tk.Label(
                        message_frame,
                        text=secondary_message,
                        bg='#A5D6A7',
                        fg='#555555',
                        font=("Arial", 30),
                        wraplength=1200
                    )
                    secondary_label.pack(pady=(10, 0))
                else:
                    main_label = tk.Label(
                        message_frame,
                        text=secondary_message,
                        bg='#A5D6A7',
                        fg='black',
                        font=("Arial", 25, "bold"),
                        wraplength=1200
                    )
                    main_label.pack()

                    secondary_label = tk.Label(
                        message_frame,
                        text=main_message,
                        bg='#A5D6A7',
                        fg='#555555',
                        font=("Arial", 20),
                        wraplength=1000
                    )
                    secondary_label.pack(pady=(10, 0))

                self.display_animal_images(group_name, message_frame)
            
            if rule_found == True:
                break


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
