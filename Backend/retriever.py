import json
import os


def retrieve(query):

    base_dir = os.path.dirname(
        os.path.dirname(__file__)
    )

    file_path = os.path.join(
        base_dir,
        "Data",
        "questions.json"
    )

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    results = []

    query = query.lower()

    for category in data.values():

        for item in category:

            question = item["question"].lower()

            if query in question:

                results.append(item)

    return results