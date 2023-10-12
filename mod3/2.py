import csv
import re


class Skill:
    def __init__(self, keywords):
        self.keywords = keywords

    def process_row(self, row):
        return [self.process_field(text) for text in row]

    def process_field(self, field_text):
        field_text = self.process_html_tags(field_text);field_text = self.process_keywords(field_text)
        field_text = self.process_time(field_text);field_text = self.process_date(field_text)
        return field_text

    @staticmethod
    def process_html_tags(field_text):
        return re.sub('<.*?>', '', field_text)

    def process_keywords(self, field_text):
        for word in self.keywords:
            field_text = re.sub(r'\w*{}\w*'.format(word),
                                lambda x: x[0].upper(),
                                field_text,
                                flags=re.IGNORECASE)
        return field_text

    @staticmethod
    def process_time(field_text):
        return re.sub(r'([0-2][0-9])\.([0-5][0-9])', r'\1:\2', field_text)

    @staticmethod
    def process_date(field_text):
        return re.sub(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})([+-]\d{4})",
                      r"\4-\5-\6\7 \3/\2/\1",
                      field_text)


def refactor_csv_file(file, new_file, keywords):
    processor = Skill(keywords)
    with open(file, 'r', encoding='utf-8') as input_file, open(new_file, 'w', encoding='utf-8') as output_file:
        reader = csv.reader(input_file)
        writer = csv.writer(output_file, lineterminator='\n')
        for row in reader:
            writer.writerow(processor.process_row(row))


file = input()
new_file = input()
keywords_list = input().split(',')
refactor_csv_file(file, new_file, keywords_list)
