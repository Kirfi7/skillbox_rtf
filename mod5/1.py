import re
import csv
from prettytable import PrettyTable, ALL


class CSVHandler:
    def __init__(self, work_experience, currencies):
        self.work_experience = work_experience
        self.currencies = currencies

    def replace_tags_spaces(self, row):
        for cell in row:
            string = re.sub(r'\<[^>]*\>', '', row[cell])
            if cell == 'key_skills':
                string = string.split('\n')
                string = filter(lambda x: x != '', string)
                string = [re.sub(r'\s+', ' ', elem) for elem in string]
                string = [elem.strip() for elem in string]
            else:
                string = re.sub(r'\s+', ' ', string.strip())
            row[cell] = string
        return row

    def read_csv(self, filename):
        file = open(filename, encoding='utf-8-sig')
        file_reader = csv.DictReader(file)
        return list(file_reader), file_reader.fieldnames

    def get_new_clear_csv(self, reader):
        new_csv = []
        for vacancy_dict in reader:
            if all(vacancy_dict.values()):
                vacancy = self.replace_tags_spaces(vacancy_dict)
                new_csv.append(vacancy)
        return new_csv

    def update_csv(self, csv):
        for row in csv:
            row['key_skills'] = '\n'.join(row['key_skills'])
            row['experience_id'] = self.work_experience[row['experience_id']]
            row['salary_currency'] = self.currencies[row['salary_currency']]
            row['premium'] = 'Да' if row['premium'] in ['TRUE', 'True'] else 'Нет'
            row['salary_gross'] = 'Без вычета налогов' if row['salary_gross'] in ['TRUE', 'True'] else 'С вычетом налогов'
            row['salary_from'] = f'{int(row["salary_from"].replace(".0", "")):,}'.replace(',', ' ')
            row['salary_to'] = f'{int(row["salary_to"].replace(".0", "")):,}'.replace(',', ' ')
            row['salary'] = f'{row["salary_from"]} - {row["salary_to"]}  ({row["salary_currency"]}) ({row["salary_gross"]})'
            row['published_at'] = f'{(row["published_at"][:10])[8:10]}.{(row["published_at"][:10])[5:7]}.{(row["published_at"][:10])[:4]}'
        return csv


class PrettyTableHandler:
    def __init__(self):
        self.my_table = PrettyTable()

    def get_table(self, filename, csv_handler):
        self.my_table.field_names = ['№', 'Название', 'Описание', 'Навыки', 'Опыт работы', 'Премиум-вакансия',
                                     'Компания', 'Оклад', 'Название региона', 'Дата публикации вакансии']
        self.my_table.align = 'l'
        self.my_table.hrules = ALL
        self.my_table.max_width = 20

        reader, fieldnames = csv_handler.read_csv(filename)
        csv = csv_handler.get_new_clear_csv(reader)
        csv = csv_handler.update_csv(csv)

        is_empty = ''
        if not fieldnames:
            is_empty = 'Пустой файл'
        elif fieldnames and len(csv) == 0:
            is_empty = 'Нет данных'

        for index, row in enumerate(csv):
            added_row = [index + 1, row['name'], row['description'], row['key_skills'], row['experience_id'],
                         row['premium'], row['employer_name'], row['salary'], row['area_name'], row['published_at']]
            self.my_table.add_row([str(cell)[:100] + '...' if len(str(cell)) > 100 else cell for cell in added_row])

        def filtrate_table(indexes, fields):
            if is_empty:
                return print(is_empty)
            fields = ['№'] + fields.split(', ') if len(fields) > 0 else fields
            match len(indexes):
                case 0:
                    return print(self.my_table.get_string(fields=fields))
                case 1:
                    return print(self.my_table.get_string(start=int(indexes) - 1, fields=fields))
                case _:
                    start_ind, end_ind = (int(x) for x in indexes.split())
                    return print(self.my_table.get_string(start=start_ind - 1, end=end_ind - 1, fields=fields))

        return filtrate_table


work_experience = {
    "noExperience": "Нет опыта",
    "between1And3": "От 1 года до 3 лет",
    "between3And6": "От 3 до 6 лет",
    "moreThan6": "Более 6 лет",
}

currencies = {
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

filename = input()
csv_handler = CSVHandler(work_experience, currencies)
pretty_table_handler = PrettyTableHandler()
my_table = pretty_table_handler.get_table(filename, csv_handler)

indexes = input()
fieldnames = input()
my_table(indexes, fieldnames)
