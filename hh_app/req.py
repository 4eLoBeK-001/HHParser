from pprint import pprint

import requests

url = "https://api.hh.ru/vacancies"

params = {
    "text": "Python разработчик",  # поиск по ключевым словам
    "area": 113,  # регион (1 = Москва, 2 = Санкт-Петербург, 113 = Россия)
    "per_page": 10,  # сколько вакансий на страницу
    "page": 1,  # номер страницы
    "only_with_salary": True  # фильтрация только по зарплате
}

response = requests.get(url=url, params=params)
response = response.json()

print(response)
for item in response.get('items'):
    pprint(item.get('snippet'))
    pprint(item.get('professional_roles'))
    print()
