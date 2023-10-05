import csv
import re
from collections import Counter
from statistics import mean


def get_average_salary(vacancy):
    salary_from = int(vacancy['salary_from'])
    salary_to = int(vacancy['salary_to']) if vacancy['salary_to'] else None
    return (salary_from + salary_to) // 2 if salary_to else salary_from


def pluralize(count, forms):
    if count % 10 == 1 and count % 100 != 11:
        return forms[0]
    elif 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
        return forms[1]
    else:
        return forms[2]


def print_top_vacancies(title, vacancies_list, top_n=10):
    print(title)
    vacancies_list.sort(key=lambda x: get_average_salary(x), reverse=(title == "Самые высокие зарплаты"))

    for i, vacancy in enumerate(vacancies_list[:top_n], start=1):
        avg_salary = get_average_salary(vacancy)
        name = vacancy['name']
        employer = re.sub(r'<[^>]+>', '', vacancy['employer_name'])
        city = vacancy['area_name']
        print(
            f"    {i}) {name} в компании \"{employer}\" - {avg_salary} {pluralize(avg_salary, ['рубль', 'рубля', 'рублей'])} (г. {city})")


def main():
    vacancies = []
    with open('vacancies.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            vacancies.append(row)

    rub_vacancies = [v for v in vacancies if v['salary_currency'] == 'RUR']

    print_top_vacancies("Самые высокие зарплаты:", rub_vacancies[:10])
    print()
    print_top_vacancies("Самые низкие зарплаты:", rub_vacancies[:10][::-1])
    print()

    key_skills = [skill for vacancy in rub_vacancies for skill in vacancy['key_skills'].split('\\n') if skill]
    skill_counts = Counter(key_skills)

    print(f"Из {len(skill_counts)} скиллов, самыми популярными являются:")
    for i, (skill, count) in enumerate(skill_counts.most_common(10), start=1):
        skill = re.sub(r'["”\']', '', skill.strip())
        print(f"    {i}) {skill} - упоминается {count} раз{pluralize(count, ['', 'а', ''])}")
    print()

    city_salaries = {}
    for vacancy in rub_vacancies:
        city = vacancy['area_name']
        salary = get_average_salary(vacancy)
        city_salaries.setdefault(city, []).append(salary)

    city_averages = {city: int(mean(salaries)) for city, salaries in city_salaries.items()}
    sorted_city_averages = sorted(city_averages.items(), key=lambda x: x[1], reverse=True)

    print(f"Из {len(sorted_city_averages)} городов, самые высокие средние ЗП:")
    for i, (city, avg_salary) in enumerate(sorted_city_averages[:10], start=1):
        vacancy_count = len(city_salaries[city])
        print(
            f"    {i}) {city} - средняя зарплата {avg_salary} {pluralize(avg_salary, ['рубль', 'рубля', 'рублей'])} ({vacancy_count} ваканси{pluralize(vacancy_count, ['я', 'и', 'й'])})")


if __name__ == "__main__":
    main()
