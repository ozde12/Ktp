import json

# Load the knowledge base
with open('knowledge_base.json', 'r') as file:
    knowledge_base = json.load(file)

rules = knowledge_base["Rules"]
facts = set()  # Holds user-provided facts

# Function to ask a question and record the answer
def ask_question(feature):
    response = input(f"{feature['question']} (yes/no): ").strip().lower()
    return response == "yes"

# Function to evaluate rules recursively
def evaluate_rules(rule_set, current_group):
    for rule in rule_set:
        if rule["current animal group"] == current_group:
            features = rule.get("features", [])
            if len(features) == 2:  # Two features in the rule
                results = [f in facts for f in features]
                if all(results) and "bothTrue" in rule:
                    return rule["bothTrue"]
                elif not any(results) and "bothFalse" in rule:
                    return rule["bothFalse"]
                elif any(results) and "oneTrue" in rule:
                    return rule["oneTrue"]
            elif len(features) == 1:  # Single feature in the rule
                feature = features[0]
                if feature in facts and "true" in rule:
                    return rule["true"]
                elif feature not in facts and "false" in rule:
                    return rule["false"]
    return None  # If no rule applies

# Start the classification process
def classify_animal():
    current_group = "animal"
    while True:
        # Evaluate the current group
        next_group = evaluate_rules(rules, current_group)
        if isinstance(next_group, str):  # Final group or question number
            if next_group.isdigit():  # If it's a question, ask it
                question_index = int(next_group) - 1
                question_feature = knowledge_base["Facts"][question_index]
                feature_data = next(
                    (f for group in knowledge_base["Knowledge base"]
                     for f in group["features"] if f["name"] == question_feature), None
                )
                if ask_question(feature_data):
                    facts.add(question_feature)
                else:
                    facts.discard(question_feature)
            else:  # If it's a group, classification is complete
                print(f"The animal belongs to the group: {next_group}")
                break
        elif isinstance(next_group, list):  # If it's a list, move to the next questions
            current_group = next_group
        else:
            print("No matching rule found.")
            break

# Run the script
if __name__ == "__main__":
    classify_animal()
