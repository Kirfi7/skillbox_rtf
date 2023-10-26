import re
import csv
from prettytable import PrettyTable, ALL

class VacancyProcessor:
    def __init__(self):
        self.work_experience = {
            "noExperience": "Нет опыта",
            "between1And3": "От 1 года до 3 лет",
            "between3And6": "От 3 до 6 лет",
            "moreThan6": "Более 6 лет",
        }

        self.currencies = {
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

        self.fieldnames = {
            'Название': 'name',
            'Описание': 'description',
            'Навыки': 'key_skills',
            'Опыт работы': 'experience_id',
            'Премиум-вакансия': 'premium',
            'Компания': 'employer_name',
            'Нижняя граница вилки оклада': 'salary_from',
            'Верхяя граница вилки оклада': 'salary_to',
            'Оклад указан до вычета налогов': 'salary_gross',
            'Идентификатор валюты оклада': 'salary_currency',
            'Название региона': 'area_name',
            'Дата публикации вакансии': 'published_at',
            'Оклад': 'salary',
        }

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
            row['salary'] = f'{row["salary_from"]} - {row["salary_to"]} ({row["salary_currency"]}) ({row["salary_gross"]})'
            row['published_at'] = f'{(row["published_at"][:10])[8:10]}.{(row["published_at"][:10])[5:7]}.{(row["published_at"][:10])[:4]}'
        return csv

    def check_row_for_filter(self, filter_string, row):
        match filter_string[0]:
            case 'Оклад':
                if int(row['salary_from'].replace(' ', '')) <= int(filter_string[1]) <= int(row['salary_to'].replace(' ', '')):
                    return True
            case 'Навыки':
                if all(x in row['key_skills'].split('\n') for x in filter_string[1].split(', ')):
                    return True
            case _:
                if row[self.fieldnames[filter_string[0]]] == filter_string[1]:
                    return True
        return False

    def get_table(self, filename):
        my_table = PrettyTable()
        my_table.field_names = ['№', 'Название', 'Описание', 'Навыки', 'Опыт работы', 'Премиум-вакансия',
                                'Компания', 'Оклад', 'Название региона', 'Дата публикации вакансии']
        my_table.align = 'l'
        my_table.hrules = ALL
        my_table.max_width = 20

        reader, fieldnames_csv = self.read_csv(filename)
        csv = self.get_new_clear_csv(reader)
        csv = self.update_csv(csv)

        is_empty = ''
        if not fieldnames_csv:
            is_empty = 'Пустой файл'
        elif fieldnames_csv and len(csv) == 0:
            is_empty = 'Нет данных'

        def filtrate_table(filter_string, indexes, fields):
            if is_empty:
                return print(is_empty)

            match filter_string:
                case '':
                    for index, row in enumerate(csv):
                        added_row = [index + 1, row['name'], row['description'], row['key_skills'], row['experience_id'],
                                     row['premium'], row['employer_name'], row['salary'], row['area_name'], row['published_at']]
                        my_table.add_row([str(cell)[:100] + '...' if len(str(cell)) > 100 else cell for cell in added_row])
                case _:
                    if ': ' not in filter_string:
                        return print('Формат ввода некорректен')

                    filter_string = filter_string.split(': ')

                    if filter_string[0] not in self.fieldnames.keys():
                        return print('Параметр поиска некорректен')

                    counter = 0
                    for index, row in enumerate(csv):
                        if (self.check_row_for_filter(filter_string, row)):
                            counter += 1
                            added_row = [counter, row['name'], row['description'],row['key_skills'], row['experience_id'],
                                         row['premium'], row['employer_name'], row['salary'], row['area_name'], row['published_at']]
                            my_table.add_row([str(cell)[:100] + '...' if len(str(cell)) > 100 else cell for cell in added_row])

                    if counter == 0:
                        return print('Ничего не найдено')


            fields = ['№'] + fields.split(', ') if len(fields) > 0 else fields
            match len(indexes):
                case 0:
                    return print(my_table.get_string(fields=fields))
                case 1:
                    return print(my_table.get_string(start=int(indexes) - 1, fields=fields))
                case _:
                    start_ind, end_ind = (int(x) for x in indexes.split())
                    return print(my_table.get_string(start=start_ind - 1, end=end_ind - 1, fields=fields))

        return filtrate_table


filename = input()
vacancy_processor = VacancyProcessor()
my_table = vacancy_processor.get_table(filename)

filter_input = input()
indexes = input()
fieldnames_input = input()
my_table(filter_input, indexes, fieldnames_input)
