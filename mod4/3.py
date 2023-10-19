import re
import csv
from prettytable import PrettyTable, ALL


class DataProcessor:
    WORK_EXPERIENCE = {
        "noExperience": "Нет опыта",
        "between1And3": "От 1 года до 3 лет",
        "between3And6": "От 3 до 6 лет",
        "moreThan6": "Более 6 лет",
    }

    CURRENCIES = {
        "AZN": "Манаты",
        "BYR": "Белорусские рубли",
        "EUR": "Евро",
        "GEL": "Грузинский лари",
        "KGS": "Киргизский сом",
        "KZT": "Тенге",
        "RUR": "Рубли",
        "UAH": "Гривны",
        "USD": "Доллары",
        "UZS": "Узбекский сум",
    }

    @staticmethod
    def replace_tags_spaces(row):
        for key, value in row.items():
            if key == 'key_skills':
                value = [re.sub(r'\s+', ' ', elem.strip()) for elem in value.split('\n') if elem.strip()]
            else:
                value = re.sub(r'\s+', ' ', re.sub(r'<[^>]*>', '', value)).strip()
            row[key] = value
        return row

    @staticmethod
    def read_csv(filename):
        with open(filename, encoding='utf-8-sig') as file:
            file_reader = csv.DictReader(file)
            return list(file_reader), file_reader.fieldnames

    def get_new_clear_csv(self, reader):
        return [self.replace_tags_spaces(vacancy) for vacancy in reader if all(vacancy.values())]

    def update_csv(self, csv):
        for row in csv:
            row['key_skills'] = '\n'.join(row['key_skills'])
            row['experience_id'] = self.WORK_EXPERIENCE[row['experience_id']]
            row['salary_currency'] = self.CURRENCIES[row['salary_currency']]
            row['premium'] = 'Да' if row['premium'].lower() == 'true' else 'Нет'
            row['salary_gross'] = 'Без вычета налогов' if row['salary_gross'].lower() == 'true' else 'С вычетом налогов'
            row['salary_from'] = f"{int(float(row['salary_from'])):,}".replace(',', ' ')
            row['salary_to'] = f"{int(float(row['salary_to'])):,}".replace(',', ' ')
            row['salary'] = f"{row['salary_from']} - {row['salary_to']} ({row['salary_currency']}) ({row['salary_gross']})"
            row['published_at'] = f"{row['published_at'][:10][-2:]}.{row['published_at'][:10][5:7]}.{row['published_at'][:4]}"
        return csv

    def get_table(self, filename):
        my_table = PrettyTable()
        my_table.field_names = ['№', 'Название', 'Описание', 'Навыки', 'Опыт работы', 'Премиум-вакансия',
                                'Компания', 'Оклад', 'Название региона', 'Дата публикации вакансии']
        my_table.align = 'l'
        my_table.hrules = ALL
        my_table.max_width = 20

        reader, fieldnames = self.read_csv(filename)
        csv = self.get_new_clear_csv(reader)
        if not fieldnames:
            print('Пустой файл')
        elif not csv:
            print('Нет данных')
        else:
            csv = self.update_csv(csv)
            for index, row in enumerate(csv):
                added_row = [index + 1, row['name'], row['description'], row['key_skills'], row['experience_id'],
                             row['premium'], row['employer_name'], row['salary'], row['area_name'], row['published_at']]
                row_data = [str(cell)[:100] + '...' if len(str(cell)) > 100 else cell for cell in added_row]
                my_table.add_row(row_data)
            print(my_table)


if __name__ == "__main__":
    data_processor = DataProcessor()
    filename = input()
    data_processor.get_table(filename)
