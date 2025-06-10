import json
import os
import io

import spacy
import pymupdf

from app.exceptions.internship_listings_exceptions import spaCyDown

nlp = None
skills_set = set()

current_dir = os.path.dirname(__file__)

def load_nlp():
    global nlp
    if nlp is None:
        nlp = spacy.load("en_core_web_sm")

def load_skills():
    global skills_set
    if not skills_set:
        json_path = os.path.join(current_dir, "programming_technologies.json")
        with open(json_path, "r") as file:
            dict_list = json.load(file)
            for dict in dict_list:
                skills_set.add(dict["name"].lower())

async def get_skills(file: io.BytesIO):
    """Retrieve skills from user's resume"""
    try:
        doc = pymupdf.open(stream=file, filetype="pdf")
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
        return list(result)
    except Exception as e:
        raise spaCyDown from e
