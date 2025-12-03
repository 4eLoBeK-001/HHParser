import time

from rest_framework import status
from django.core.management.base import BaseCommand
import requests
from pprint import pprint

from hh_app.utils.session import HHSession
from utils.utils import create_vacancy, skill_list


class Command(BaseCommand):
    help = "Парсит вакансии с hh.ru и сохраняет их в БД"

    def handle(self, *args, **options):
        url = "https://api.hh.ru/vacancies"

        params = {
            "text": "Python разработчик",
            "area": 113,
            "per_page": 50,
            "page": 0,
            "only_with_salary": "True",
            "order_by": "publication_time"
        }

        stop = False

        while True:
            session = HHSession.get().get(url, params=params, timeout=15)

            if session.status_code == status.HTTP_200_OK:
                data = session.json()
                found = data.get('found', 0)

                for item in data.get('items'):
                    is_new = create_vacancy(item, params)
                    
                    if not is_new:
                        stop = True
                        break
                    time.sleep(0.3)
                
                if stop:
                    print('цикл прерван')
                    break

                time.sleep(3)

                params['page'] += 1
                if params['page'] > data.get('pages', 0):
                    break

        print('Парсинг завершён. Всего', found, 'вакансий')
