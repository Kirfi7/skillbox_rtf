import json
import re

class Skill:
    @staticmethod
    def process_field(field_text: str, result: dict) -> None:
        if not field_text:
            return

        header, data = [i.strip() for i in field_text.split(':')]
        if header in Skill.field_processors:
            result[header] = Skill.field_processors[header](data)

    @staticmethod
    def process_description(data: str) -> str:
        def capitalize_sentence(sentence: str) -> str:
            words = [word.capitalize() if i == 0 else word.lower() for i, word in enumerate(sentence.split())]
            return ' '.join(words)

        sentences = [capitalize_sentence(sent.strip()) for sent in data.split('.') if sent.strip()]
        return ". ".join(sentences)

    @staticmethod
    def process_salary(data: str) -> str:
        return "{:.3f}".format(float(data))

    @staticmethod
    def process_key_phrase(data: str) -> str:
        return data.upper() + '!'

    @staticmethod
    def process_addition(data: str) -> str:
        return "..." + data.lower() + "..."

    @staticmethod
    def process_reverse(data: str) -> str:
        return data[::-1]

    @staticmethod
    def process_company_info(data: str) -> str:
        while re.search(r'\([^()]*\)', data):
            data = re.sub(r'\([^()]*\)', '', data)

        return data

    @staticmethod
    def process_key_skills(data: str) -> str:
        return re.sub('&nbsp', ' ', data, flags=re.IGNORECASE)

    field_processors = {
        "description": process_description,
        "salary": process_salary,
        "key_phrase": process_key_phrase,
        "addition": process_addition,
        "reverse": process_reverse,
        "company_info": process_company_info,
        "key_skills": process_key_skills,
    }

def get_data(input_text, headings_text):
    output_headings = headings_text.split(", ")
    fields = [i.strip() for i in input_text.split(';')]
    processed = dict()
    ans = Skill()
    for field in fields:
        ans.process_field(field, processed)
    return json.dumps({key: value for key, value in processed.items() if key in output_headings})

input_text = input()
headings = input()

print(get_data(input_text, headings))
