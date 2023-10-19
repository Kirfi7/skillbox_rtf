import re
import csv


class VacancyProcessor:
    def __init__(self, filename):
        self.filename = filename
        self.list_naming = ['Название', 'Описание', 'Навыки', 'Опыт работы', 'Премиум-вакансия', 'Компания',
                            'Нижняя граница вилки оклада', 'Верхняя граница вилки оклада', 'Оклад указан до вычета налогов',
                            'Идентификатор валюты оклада', 'Название региона', 'Дата и время публикации вакансии']
        self.result_fieldnames = {}
        self.data_vacancies = []

    def replace_tags_symbols(self, string):
        string = re.sub(r'<[^>]*>', '', string)
        if '\n' in string:
            string = string.split('\n')
            string = [re.sub(r'\s+', ' ', elem.strip()) for elem in string]
            string = [elem.strip() for elem in string]
            string = ', '.join(string)
        elif string.lower() in ['false', 'true']:
            string = 'Нет' if string.lower() == 'false' else 'Да'
        else:
            string = re.sub(r'\s+', ' ', string.strip())
        return string

    def clear_vacancy_dict(self, vacancy_dict):
        for cell in vacancy_dict:
            vacancy_dict[cell] = self.replace_tags_symbols(vacancy_dict[cell])

    def csv_reader(self):
        with open(self.filename, encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            fieldnames = reader.fieldnames
            for index, name in enumerate(fieldnames):
                self.result_fieldnames[name] = self.list_naming[index]
            for row in reader:
                if all(row.values()):
                    self.data_vacancies.append(row)

    def process_vacancies(self):
        for vacancy in self.data_vacancies:
            self.clear_vacancy_dict(vacancy)

    def print_vacancies(self):
        for index, vacancy in enumerate(self.data_vacancies):
            for name in self.result_fieldnames:
                print(f'{self.result_fieldnames[name]}: {vacancy[name]}')
            if len(self.data_vacancies) > 1 and index < len(self.data_vacancies) - 1:
                print()


file = input()
vacancy_processor = VacancyProcessor(file)
vacancy_processor.csv_reader()
vacancy_processor.process_vacancies()
vacancy_processor.print_vacancies()
