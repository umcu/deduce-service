import json


def load_single_example_text():
    with open("test/data/single_text.json") as json_file:
        return json.load(json_file)


def load_multiple_example_texts():
    with open("test/data/multiple_texts.json") as json_file:
        return json.load(json_file)
