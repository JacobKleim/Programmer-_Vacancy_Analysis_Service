import os

import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable


LANGUAGES = ['python', 'javascript', 'java', 'ruby', 'php', 'c++', 'c#', 'c']


def get_average_salary(to_value, from_value):

    if not to_value and from_value:
        average_value = from_value * 1.2
    elif not from_value and to_value:
        average_value = to_value * 0.8
    elif not from_value and not to_value:
        return None
    else:
        average_value = (from_value + to_value) / 2
    return int(average_value)


def predict_rub_salary_for_headhunter(vacancy):
    salary = vacancy['salary']
    to_value = salary['to']
    from_value = salary['from']

    if salary['currency'] != 'RUR':
        return None

    return get_average_salary(to_value, from_value)


def predict_rub_salary_for_superjob(vacancy):
    to_value = vacancy['payment_to']
    from_value = vacancy['payment_from']

    if vacancy['currency'] != 'rub':
        return None

    return get_average_salary(to_value, from_value)


def get_headhunter_vacancy_statistics(language):
    city = 1
    period = 30
    url = 'https://api.hh.ru/vacancies'
    vacancies_average_salaries = []
    page = 0
    pages_number = 1
    all_pages = []

    while page < pages_number:
        try:
            params = {'text': f'программист {language}',
                      'area': city,
                      'period': period,
                      'page': page}
            page_response = requests.get(url, params=params)
            page_response.raise_for_status()
            page_content = page_response.json()
            total_pages = page_content['pages']
            pages_number = total_pages

            if not page_content['items']:
                break

            all_pages.append(page_content)
            page += 1
        except requests.exceptions.HTTPError as e:
            print(e)

    all_vacancies = []

    for page in all_pages:
        response_found = page['found']
        all_vacancies.extend(page['items'])

    language_statistics = {'vacancies_found': response_found}

    for vacancy in all_vacancies:
        salary = vacancy['salary']
        if not salary:
            continue
        vacancy_average_salary = predict_rub_salary_for_headhunter(
            vacancy)
        if vacancy_average_salary:
            vacancies_average_salaries.append(
                vacancy_average_salary)

    vacancies_processed_number = len(vacancies_average_salaries)
    language_statistics['vacancies_processed'] = vacancies_processed_number

    if vacancies_processed_number:
        language_statistics["average_salary"] = int(sum(
            vacancies_average_salaries) / vacancies_processed_number)

    return language_statistics


def get_superjob_vacancy_statistics(token, language):
    city = 4
    vacancies_average_salaries = []
    page = 0
    url = 'https://api.superjob.ru/2.0/vacancies/'
    all_pages = []

    while True:
        try:
            params = {'keyword': f'Программист {language}',
                      'town': city,
                      'page': page}
            header = {'X-Api-App-Id': token}
            page_response = requests.get(url, params=params,
                                         headers=header)
            page_content = page_response.json()
            page_response.raise_for_status()

            if 'objects' not in page_content:
                break

            all_pages.append(page_content)

            if not page_content['more']:
                break

            page += 1
        except requests.exceptions.HTTPError as e:
            print(e)

    all_vacancies = []

    for page in all_pages:
        response_found = page['total']
        all_vacancies.extend(page['objects'])

    language_statistics = {'vacancies_found': response_found}

    for vacancy in all_vacancies:
        vacancy_average_salary = predict_rub_salary_for_superjob(
            vacancy)
        if vacancy_average_salary:
            vacancies_average_salaries.append(vacancy_average_salary)

    vacancies_processed_number = len(vacancies_average_salaries)
    language_statistics['vacancies_processed'] = vacancies_processed_number

    if vacancies_processed_number:
        language_statistics['average_salary'] = int(sum(
            vacancies_average_salaries) / vacancies_processed_number)

    return language_statistics


def output_table(language_statistics):
    table = [
        ['Язык программирования',
         'Вакансий найдено',
         'Вакансий обработано',
         'Средняя зарплата'],
    ]

    for language in language_statistics:
        language_info = language_statistics[language]
        if language_info['vacancies_found']:
            vacancies_found = language_info['vacancies_found']
            vacancies_processed = language_info['vacancies_processed']
            average_salary = language_info['average_salary']
        else:
            vacancies_found = 0
            vacancies_processed = 0
            average_salary = 0

        info = [
                language,
                vacancies_found,
                vacancies_processed,
                average_salary
            ]

        table.append(info)

    return table


def main():
    load_dotenv()

    sj_token = os.getenv('SJ_TOKEN')

    hh_languages_statistics = {}
    sj_languages_statistics = {}

    for language in LANGUAGES:
        hh_languages_statistics[language] = get_headhunter_vacancy_statistics(
            language)

        sj_languages_statistics[language] = get_superjob_vacancy_statistics(
            sj_token,
            language)

    hh_formatted_statistics = output_table(hh_languages_statistics)
    table_hh = AsciiTable(hh_formatted_statistics, 'HeadHunter Moscow')
    table_hh.justify_columns[2] = 'right'
    print(table_hh.table)

    sj_formatted_statistics = output_table(sj_languages_statistics)
    table_sj = AsciiTable(sj_formatted_statistics, 'SuperJob Moscow')
    table_sj.justify_columns[2] = 'right'
    print(table_sj.table)


if __name__ == '__main__':
    main()
