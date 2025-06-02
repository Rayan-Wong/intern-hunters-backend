import json
import os
import asyncio

import spacy
import pymupdf

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

async def get_skills():
    """Retrieve skills from user's resume"""
    try:
        load_nlp()
        load_skills()
        pdf_path = os.path.join(current_dir, "test_resume.pdf")
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
    except:
        pass

print(asyncio.run(get_skills()))