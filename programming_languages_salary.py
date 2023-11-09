import json
import os

import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable


languages = ['python', 'javascript', 'java', 'ruby', 'php', 'c++', 'c#', 'c']


def predict_rub_salary_for_headhunter(item):
    salary = item['salary']
    if salary['currency'] == 'RUR':
        if salary['to'] is None:
            average_value = salary['from'] * 1.2
        elif salary['from'] is None:
            average_value = salary['to'] * 0.8
        else:
            average_value = (salary['from'] + salary['to']) / 2
    else:
        return None

    return int(average_value)


def predict_rub_salary_for_superjob(vacancy):

    if vacancy['currency'] == 'rub':
        if vacancy['payment_to'] == 0 and vacancy['payment_from'] != 0:
            average_value = vacancy['payment_from'] * 1.2
        elif vacancy['payment_from'] == 0 and vacancy['payment_to'] != 0:
            average_value = vacancy['payment_to'] * 0.8
        elif vacancy['payment_from'] == 0 and vacancy['payment_to'] == 0:
            return None
        else:
            average_value = (
                vacancy['payment_from'] + vacancy['payment_to']) / 2
    else:
        return None

    return int(average_value)


def get_headhunter_vacancy_statistics():
    statistics_by_languages_hh = {}
    city = 1
    period = 30

    for language in languages:
        average_salary_for_vacancies = []
        page = 0
        pages_number = 50
        all_pages = []

        while page < pages_number:
            try:
                params = {'text': f'программист {language}',
                          'area': city,
                          'period': period,
                          'page': page}
                url = 'https://api.hh.ru/vacancies'
                page_response = requests.get(url, params=params)
                page_response.raise_for_status()
                page_content = json.loads(page_response.text)
                page += 1
                all_pages.append(page_content)
            except requests.exceptions.HTTPError as e:
                print(e)

        all_vacansies = []
        language_statistics = {}

        for page in all_pages:
            response_found = page['found']
            language_statistics['vacancies_found'] = response_found
            for items in page['items']:
                all_vacansies.append(items)

        for item in all_vacansies:
            salary = item['salary']
            if salary is not None:
                average_salary_for_vacancy = predict_rub_salary_for_headhunter(
                    item)
                if average_salary_for_vacancy is not None:
                    average_salary_for_vacancies.append(
                        average_salary_for_vacancy)

        vacancies_processed_number = len(average_salary_for_vacancies)
        language_statistics['vacancies_processed'] = vacancies_processed_number

        if vacancies_processed_number > 0:
            language_statistics["average_salary"] = int(sum(
                average_salary_for_vacancies) / vacancies_processed_number)
        else:
            language_statistics["average_salary"] = None

        statistics_by_languages_hh[f"{language}"] = language_statistics
    return statistics_by_languages_hh


def get_superjob_vacancy_statistics(token):
    languages_statistics_sj = {}
    city = 4
    for language in languages:
        average_salary_for_vacancies = []
        page = 0
        pages_number = 30
        all_pages = []

        while page < pages_number:
            try:
                params = {'keyword': f'Программист {language}',
                          'town': city,
                          'page': page}
                header = {'X-Api-App-Id': token}
                url = 'https://api.superjob.ru/2.0/vacancies/'
                page_response = requests.get(url, params=params,
                                             headers=header)
                page_content = json.loads(page_response.text)
                page_response.raise_for_status()
                page += 1
                all_pages.append(page_content)
            except requests.exceptions.HTTPError as e:
                print(e)

        all_vacansies = []
        language_statistics = {}

        for page in all_pages:
            response_found = page['total']
            if response_found != 0:
                language_statistics['vacancies_found'] = response_found

            for items in page['objects']:
                all_vacansies.append(items)

        average_salary_for_vacancies = []

        for vacancy in all_vacansies:
            average_salary_for_vacancy = predict_rub_salary_for_superjob(
                vacancy)
            if average_salary_for_vacancy is not None:
                average_salary_for_vacancies.append(average_salary_for_vacancy)

        vacancies_processed_number = len(average_salary_for_vacancies)
        language_statistics['vacancies_processed'] = vacancies_processed_number
        if vacancies_processed_number > 0:
            language_statistics['average_salary'] = int(sum(
                average_salary_for_vacancies) / vacancies_processed_number)
        else:
            language_statistics['average_salary'] = None
        languages_statistics_sj[f"{language}"] = language_statistics

    return languages_statistics_sj


def output_table(language_statistics):
    table = [
        ['Язык программирования',
         'Вакансий найдено',
         'Вакансий обработано',
         'Средняя зарплата'],
    ]

    for language in language_statistics:
        language_info = language_statistics[f'{language}']
        try:
            vacancies_found = language_info['vacancies_found']
            vacancies_processed = language_info['vacancies_processed']
            average_salary = language_info['average_salary']
        except KeyError:
            vacancies_found = 0
            vacancies_processed = 0
            average_salary = 0

        info = [
                f'{language}',
                f'{vacancies_found}',
                f'{vacancies_processed}',
                f'{average_salary}'
            ]

        table.append(info)

    return table


def main():
    load_dotenv()

    sj_token = os.getenv('SJ_TOKEN')

    table_hh = AsciiTable(output_table(get_headhunter_vacancy_statistics()),
                          'HeadHunter Moscow')
    table_hh.justify_columns[2] = 'right'
    print(table_hh.table)

    table_sj = AsciiTable(output_table(
        get_superjob_vacancy_statistics(sj_token)), 'SuperJob Moscow')
    table_sj.justify_columns[2] = 'right'
    print(table_sj.table)


if __name__ == '__main__':
    main()
