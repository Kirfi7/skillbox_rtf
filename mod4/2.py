import re
import csv

class Vacancy:
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

    def __init__(self, file_name):
        self.file_name = file_name
        self.reader, self.list_naming = self.csv_reader()
        self.data_vacancies, self.dic_naming = self.csv_filter()

    def get_fieldnames_rus(self, file_reader):
        result_dict = {}
        fieldnames_rus = ['Название', 'Описание', 'Навыки', 'Опыт работы', 'Премиум-вакансия', 'Компания',
                          'Нижняя граница вилки оклада', 'Верхняя граница вилки оклада', 'Оклад указан до вычета налогов',
                          'Идентификатор валюты оклада', 'Название региона', 'Дата публикации вакансии']
        fieldnames = file_reader.fieldnames
        for index, name in enumerate(fieldnames):
            result_dict[name] = fieldnames_rus[index]
        return result_dict

    def csv_reader(self):
        file = open(self.file_name, encoding="utf-8-sig")
        file_reader = csv.DictReader(file)
        fieldnames = self.get_fieldnames_rus(file_reader)
        return [vacancy for vacancy in file_reader if all(vacancy.values())], fieldnames

    def replace_tags_symbols(self, vacancy):
        for cell in vacancy:
            string = re.sub(r'\<[^>]*\>', '', vacancy[cell])
            if cell == "key_skills":
                string = string.split('\n')
                string = filter(lambda x: x != '', string)
                string = [re.sub(r'\s+', ' ', elem) for elem in string]
                string = ', '.join([elem.strip() for elem in string])
            else:
                string = re.sub(r'\s+', ' ', string.strip())
            if string in ['FALSE', 'TRUE'] or string in ['False', 'True']:
                string = 'Нет' if string == 'FALSE' or string == 'False' else 'Да'
            vacancy[cell] = string

    def csv_filter(self):
        for vacancy in self.reader:
            self.replace_tags_symbols(vacancy)
        return self.reader, self.list_naming

    def formatter(self, row):
        for cell in row:
            if cell in ['salary_from', 'salary_to']:
                row[cell] = row[cell].replace('.0', '')
            elif cell == 'salary_gross':
                row[cell] = 'Без вычета налогов' if row[cell] == 'Да' else 'С вычетом налогов'
            elif cell == 'salary_currency':
                row[cell] = self.currencies[row[cell]]
            elif cell == 'published_at':
                row[cell] = f'{(row[cell][:10])[8:10]}.{(row[cell][:10])[5:7]}.{(row[cell][:10])[:4]}'
            elif cell == 'experience_id':
                row[cell] = self.work_experience[row[cell]]

    def get_salary(self, salary):
        salary = f'{int(salary):,}'.replace(',', ' ')
        return salary

    def print_vacancies(self):
        for index, vacancy in enumerate(self.data_vacancies):
            self.formatter(vacancy)
            for name in self.dic_naming:
                if name == 'salary_from':
                    print(
                        f'Оклад: {self.get_salary(vacancy["salary_from"])} - {self.get_salary(vacancy["salary_to"])} ({vacancy["salary_currency"]}) ({vacancy["salary_gross"]})')
                elif name not in ['salary_from', 'salary_to', 'salary_gross', 'salary_currency']:
                    print(f'{self.dic_naming[name]}: {vacancy[name]}')
            if len(self.data_vacancies) > 1 and index < len(self.data_vacancies) - 1:
                print()


file = input()
vacancy = Vacancy(file)
vacancy.print_vacancies()
