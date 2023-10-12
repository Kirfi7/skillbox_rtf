import json
import re
from bs4 import BeautifulSoup

def extract_text_from_tag(tag):
    return re.sub(r'<.*?>', '', str(tag))

def convert_salary(salary, exchange):
    for currency, rate in exchange.items():
        if currency in salary:
            numbers = re.findall(r'\d+\s*\d+', salary)
            converted_numbers = [str(float(re.sub(r'\s', '', x)) * rate) for x in numbers]
            converted_salary = '-'.join(converted_numbers)
            return converted_salary
    return salary

html_file = input()

exchange_rates = {
    '₽': 1.0,
    '$': 100.0,
    '€': 105.0,
    '₸': 0.210,
    'Br': 30.0,
}

with open(html_file, encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

    vacancy_title = extract_text_from_tag(soup.find('div', {'class': 'vacancy-title'}).find('h1'))
    salary = extract_text_from_tag(soup.find('div', {'data-qa': 'vacancy-salary'}).find('span'))
    converted_salary = convert_salary(salary, exchange_rates)
    experience = re.sub(r'<.*?>|[A-Za-zА-Яа-я ]', '', str(soup.find('span', {'data-qa': 'vacancy-experience'}))).replace('–', '-')
    if experience == '':
        experience = None
    company = extract_text_from_tag(soup.find('span', {'class': 'vacancy-company-name'}))
    description = extract_text_from_tag(soup.find('div', {'data-qa': 'vacancy-description'}))
    skills = [extract_text_from_tag(skill) for skill in soup.find('div', {'class': 'bloko-tag-list'}).find_all('span')]
    created_at = re.sub(r'<.*?>|\s', ' ', str(soup.find('p', {'class': 'vacancy-creation-time-redesigned'}).find('span'))).strip()

    result = {
        'vacancy': vacancy_title,
        'salary': converted_salary,
        'experience': experience,
        'company': company,
        'description': description,
        'skills': ', '.join(skills),
        'created_at': created_at,
    }

    result = json.dumps(result, ensure_ascii=False)
    print(result)
