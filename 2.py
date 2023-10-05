import csv
import re


def get_processed_text(text):
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


body = []

with open("vacancies.csv", 'r', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    csv_headers = next(reader)

    for row in reader:
        row_dict = {header: get_processed_text(value) for header, value in zip(csv_headers, row)}
        if 'key_skills' in row_dict:
            row_dict['key_skills'] = row_dict['key_skills'].replace('"', '').replace('\\n', ', ').replace("”", "")
        body.append(row_dict)

for row_dict in body:
    for key, value in row_dict.items():
        print(f"{key}: {value}")
    print()
