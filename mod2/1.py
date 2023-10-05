import csv


def reader_func(filename="vacancies.csv"):
    rows_csv = []
    with open(filename, mode="r", encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=",")
        headers_csv = next(reader, [])
        for row in reader:
            if not all(row):
                continue
            rows_csv.append(row)
    return headers_csv, rows_csv


headers, rows = reader_func()
print(headers)
print(rows)
