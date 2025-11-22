from pprint import pprint

import requests

url = "https://api.hh.ru/vacancies"

params = {
    "text": "Python разработчик",  # поиск по ключевым словам
    "area": 113,  # регион (1 = Москва, 2 = Санкт-Петербург, 113 = Россия)
    "per_page": 10,  # сколько вакансий на страницу
    "page": 1,  # номер страницы
    "only_with_salary": True,  # фильтрация только по зарплате
    "order_by": "publication_time"
}

response = requests.get(url=url, params=params)
response = response.json()

print(response)
for item in response.get('items'):
    # pprint(item.get('snippet'))
    # pprint(item.get('professional_roles'))
    # print()

    print('___AREA___')
    print('id = ', item.get('area').get('id'))
    print('name = ', item.get('area').get('name'))

    print('___SALARY___')
    print('from = ', item.get('salary').get('from'))
    print('to = ', item.get('salary').get('to'))
    print('currency = ', item.get('salary').get('currency'))
    print('gross = ', item.get('salary').get('gross'))

    print('___EMPLOYER___')
    print('id = ', item.get('employer').get('id'))
    print('name = ', item.get('employer').get('name'))
    print('url = ', item.get('employer').get('alternate_url'))


    print('___WORK FORMAT___')
    if item.get('work_format') == []:
        print('code_name = ', 0)
        print('name = ', 'Не указано')
    else:
        print('code_name = ', item.get('work_format')[0].get('id'))
        print('name = ', item.get('work_format')[0].get('name'))

    print('___WORK SCHEDULE___')
    print('code_name = ', item.get('work_schedule_by_days')[0].get('id'))
    print('name = ', item.get('work_schedule_by_days')[0].get('name'))
    print('working_hours = ', item.get('working_hours')[0].get('name'))

    print('___PROFESSIONAL ROLE___')
    print('Количество ролей = ', item.get('professional_roles').__len__())
    for role in item.get('professional_roles'):
        print('name = ', role.get('name'))

    print('___SEARCH QUERY___')
    print('Ключевое слово = ', params.get('text'))

    print('___EXPERIENCE___')
    print('code_name = ', item.get('experience').get('id'))
    print('name = ', item.get('experience').get('name'))

    print('___VACANCY___')
    print('hh_vacancy_id = ', item.get('id'))
    print('name = ', item.get('name'))
    print('published_at = ', item.get('published_at'))
    print('hh_vacancy_id = ', item.get('alternate_url'))


