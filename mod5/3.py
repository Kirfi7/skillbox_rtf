import re
import csv
from prettytable import PrettyTable, ALL

work_expirence = {
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

currency_to_rub = {
    "AZN": 35.68,
    "BYR": 23.91,
    "EUR": 59.90,
    "GEL": 21.74,
    "KGS": 0.76,
    "KZT": 0.13,
    "RUR": 1,
    "UAH": 1.64,
    "USD": 60.66,
    "UZS": 0.0055,
}

fieldnames = {
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


def replace_tags_spaces(row):
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


def read_csv(filename):
    file = open(filename, encoding='utf-8-sig')
    file_reader = csv.DictReader(file)
    return list(file_reader), file_reader.fieldnames


def get_new_clear_csv(reader):
    new_csv = []
    for vacancy_dict in reader:
        if all(vacancy_dict.values()):
            vacancy = replace_tags_spaces(vacancy_dict)
            new_csv.append(vacancy)
    return new_csv


def update_csv(csv):
    for row in csv:
        row['key_skills'] = '\n'.join(row['key_skills'])
        row['experience_id'] = work_expirence[row['experience_id']]
        row['salary_currency'] = currencies[row['salary_currency']]
        row['premium'] = 'Да' if row['premium'] in ['TRUE', 'True'] else 'Нет'
        row['salary_gross'] = 'Без вычета налогов' if row['salary_gross'] in ['TRUE', 'True'] else 'С вычетом налогов'
        row['salary_from'] = f'{int(row["salary_from"].replace(".0", "")):,}'.replace(',', ' ')
        row['salary_to'] = f'{int(row["salary_to"].replace(".0", "")):,}'.replace(',', ' ')
        row['salary'] = f'{row["salary_from"]} - {row["salary_to"]} ({row["salary_currency"]}) ({row["salary_gross"]})'
        row['published_at'] = f'{(row["published_at"][:10])[8:10]}.{(row["published_at"][:10])[5:7]}.{(row["published_at"][:10])[:4]}'
    return csv


def check_row_for_filter(filter_string, row):
    match filter_string[0]:
        case 'Оклад':
            if int(row['salary_from'].replace(' ', '')) <= int(filter_string[1]) <= int(row['salary_to'].replace(' ', '')):
                return True
        case 'Навыки':
            if all(x in row['key_skills'].split('\n') for x in filter_string[1].split(', ')):
                return True
        case _:
            if row[fieldnames[filter_string[0]]] == filter_string[1]:
                return True
    return False


def get_salary_rub(row):
    if row['salary_currency'] != 'RUR':
        s_f = int(row['salary_from']) * currency_to_rub[row['salary_currency']]
        s_t = int(row['salary_to']) * currency_to_rub[row['salary_currency']]
        return (s_t + s_f) / 2
    return (int(row['salary_from']) + int(row['salary_to'])) / 2


def custom_experience_sort(item):
    order = {
        'noExperience': 0,
        'between1And3': 1,
        'between3And6': 2,
        'moreThan6': 3
    }
    return order[item['experience_id']]


def sort_csv(csv, filter, reverse_param):
    reverse = True if reverse_param == 'Да' else False
    match filter:
        case '':
            return csv
        case 'Навыки':
            sorted_csv = sorted(csv, key=lambda row: len(row['key_skills']), reverse=reverse)
        case 'Оклад':
            sorted_csv = sorted(csv, key=lambda row: get_salary_rub(row), reverse=reverse)
        case 'Дата публикации':
            sorted_csv = sorted(csv, key=lambda row: row['published_at'], reverse=reverse)
        case 'Опыт работы':
            sorted_csv = sorted(csv, key=lambda row: custom_experience_sort(row), reverse=reverse)
        case other:
            sorted_csv = sorted(csv, key=lambda row: row[fieldnames[other]], reverse=reverse)
    return sorted_csv


def get_table(filename):
    my_table = PrettyTable()
    my_table.field_names = ['№', 'Название', 'Описание', 'Навыки', 'Опыт работы', 'Премиум-вакансия',
                            'Компания', 'Оклад', 'Название региона', 'Дата публикации вакансии']
    my_table.align = 'l'
    my_table.hrules = ALL
    my_table.max_width = 20

    reader, fieldnames_csv = read_csv(filename)
    csv = get_new_clear_csv(reader)

    is_empty = ''
    if not fieldnames_csv:
        is_empty = 'Пустой файл'
    elif fieldnames_csv and len(csv) == 0:
        is_empty = 'Нет данных'

    def filtrate_table(filter_string, sorted_string, reverse_sorted_param, indexes, fields):
        if is_empty:
            return print(is_empty)

        if sorted_string not in my_table.field_names and sorted_string != '':
            return print('Параметр сортировки некорректен')
        if reverse_sorted_param not in ['Да', 'Нет', '']:
            return print('Порядок сортировки задан некорректно')

        sorted_csv = sort_csv(csv, sorted_string, reverse_sorted_param)
        final_csv = update_csv(sorted_csv)
        match filter_string:
            case '':
                for index, row in enumerate(final_csv):
                    added_row = [index + 1, row['name'], row['description'], row['key_skills'], row['experience_id'],
                                 row['premium'], row['employer_name'], row['salary'], row['area_name'], row['published_at']]
                    my_table.add_row([str(cell)[:100] + '...' if len(str(cell)) > 100 else cell for cell in added_row])
            case _:
                if ': ' not in filter_string:
                    return print('Формат ввода некорректен')

                filter_string = filter_string.split(': ')

                if filter_string[0] not in fieldnames.keys():
                    return print('Параметр поиска некорректен')

                counter = 0
                for index, row in enumerate(final_csv):
                    if check_row_for_filter(filter_string, row):
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



filename = input('Введите название файла: ')
filter_param = input('Введите параметр фильтрации: ')
sorted_param = input('Введите параметр сортировки: ')
reverse_sorted_param = input('Обратный порядок сортировки (Да / Нет): ')
indexes = input('Введите диапазон вывода: ')
fieldnames_input = input('Введите требуемые столбцы: ')

my_table = get_table(filename)
my_table(filter_param, sorted_param, reverse_sorted_param, indexes, fieldnames_input)