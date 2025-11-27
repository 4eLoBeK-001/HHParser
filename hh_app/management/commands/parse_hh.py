from datetime import datetime, timedelta
from http import HTTPStatus
import re
from rest_framework import status
from django.core.management.base import BaseCommand
import requests
from pprint import pprint

from hh_app.models import (Area, Salary, Employer, WorkFormat, WorkSchedule, 
                            ProfessionalRole, SearchQuery, Experience, Skill, Vacancy)
from utils.utils import create_vacancy, skill_list


class Command(BaseCommand):
    help = "Парсит вакансии с hh.ru и сохраняет их в БД"

    def handle(self, *args, **options):
        url = "https://api.hh.ru/vacancies"

        params = {
            "text": "Python разработчик",  # поиск по ключевым словам
            "area": 113,  # регион (1 = Москва, 2 = Санкт-Петербург, 113 = Россия)
            "per_page": 5,  # сколько вакансий на страницу
            "page": 0,  # номер страницы
            "only_with_salary": True,  # фильтрация только по зарплате
            "order_by": "publication_time"
        }

        

        response = requests.get(url=url, params=params)
        if response.status_code == status.HTTP_200_OK:
            response = response.json()
            found = response.get('found')
            print('Найдено вакансий - ', found)
            for item in response.get('items'):
                create_vacancy(item, params)

                print('Успешно')
            print('Успешно')
