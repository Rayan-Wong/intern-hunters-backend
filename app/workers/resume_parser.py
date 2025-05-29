import json
import os

import spacy
import pymupdf

nlp = spacy.load("en_core_web_sm")
skills_set = set()

current_dir = os.path.dirname(__file__)
json_path = os.path.join(current_dir, "programming_technologies.json")
pdf_path = os.path.join(current_dir, "test_resume.pdf")

with open(json_path, "r") as file:
    dict_list = json.load(file)
    for dict in dict_list:
        skills_set.add(dict["name"].lower())

def get_skills():
    """Retrieve skills from user's resume"""
    doc = pymupdf.open(pdf_path)
    text = ""
    result = set()
    for page in doc:
        text += page.get_text()
    tokens = nlp(text.lower())
    for token in tokens:
        if token.text in skills_set:
            result.add(token.text)
    for chunk in tokens.noun_chunks:
        if chunk.text in skills_set:
            result.add(chunk.text)
    return result

print(get_skills())