import json

with open('hw.json', 'r') as file:
    data = json.load(file)


print(data["message"])
