import time

from rest_framework import status
from django.core.management.base import BaseCommand
import requests
from pprint import pprint

from utils.utils import create_vacancy, skill_list


class Command(BaseCommand):
    help = "Парсит вакансии с hh.ru и сохраняет их в БД"

    def handle(self, *args, **options):
        url = "https://api.hh.ru/vacancies"
        headers = {"HH-User-Agent": "PythonHHParser/1.1 (4elobek0012@gmail.com)"}
        params = {
            "text": "Python разработчик",
            "area": 113,
            "per_page": 50,
            "page": 0,
            "only_with_salary": "True",
            "order_by": "publication_time"
        }

        while True:
            response = requests.get(url, params=params, headers=headers, timeout=15)

            if response.status_code == status.HTTP_200_OK:
                data = response.json()
                found = data.get('found', 0)

                print('Пятидесятка пошла')

                for item in data.get('items'):
                    create_vacancy(item, params)
                    time.sleep(0.3)
                time.sleep(3)

                params['page'] += 1
                if params['page'] > data.get('pages', 0):
                    break

        print('Парсинг завершён. Всего', found, 'вакансий')
