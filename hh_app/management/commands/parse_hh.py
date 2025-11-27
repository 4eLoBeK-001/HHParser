from datetime import datetime, timedelta
from http import HTTPStatus
import re
from rest_framework import status
from django.core.management.base import BaseCommand
import requests
from pprint import pprint

from hh_app.models import (Area, Salary, Employer, WorkFormat, WorkSchedule, 
                            ProfessionalRole, SearchQuery, Experience, Skill, Vacancy)
from utils.utils import skill_list


class Command(BaseCommand):
    help = "Парсит вакансии с hh.ru и сохраняет их в БД"

    def handle(self, *args, **options):
        url = "https://api.hh.ru/vacancies"

        params = {
            "text": "Python разработчик",  # поиск по ключевым словам
            "area": 113,  # регион (1 = Москва, 2 = Санкт-Петербург, 113 = Россия)
            "per_page": 10,  # сколько вакансий на страницу
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
                
                print('___AREA___')
                area = item.get('area')
                area_obj, _ = Area.objects.get_or_create(hh_area_id=area.get('id'), name=area.get('name'))
                
                print('___SALARY___')
                salary = item.get('salary')
                salary_obj, _ = Salary.objects.get_or_create(salary_from=salary.get('from'), salary_to=salary.get('to'), currency=salary.get('currency'), gross=salary.get('gross'))

                print('___EMPLOYER___')
                employer = item.get('employer')
                employer_obj, _ = Employer.objects.get_or_create(hh_employer_id=employer.get('id'), name=employer.get('name'), url=employer.get('alternate_url'))

                print('___WORK FORMAT___')
                work_format = item.get('work_format')
                if not work_format:
                    work_format_obj, _ = WorkFormat.objects.get_or_create(code_name=0, name='Не указано')
                else:
                    work_format_obj, _ = WorkFormat.objects.get_or_create(code_name=work_format[0].get('id'), name=work_format[0].get('name'))

                print('___WORK SCHEDULE___')
                work_schedule = item.get('work_schedule_by_days')
                if not work_format:
                    work_schedule_obj, _ = WorkSchedule.objects.get_or_create(code_name=0, name='Не указано', working_hours='Не указано')
                else:
                    work_schedule_obj, _ = WorkSchedule.objects.get_or_create(code_name=work_schedule[0].get('id'), name=work_schedule[0].get('name'), working_hours=work_schedule[0].get('name'))

                print('___PROFESSIONAL ROLE___')
                professional_roles = item.get('professional_roles')
                print('Количество ролей = ', professional_roles.__len__())
                lst_roles = []
                for role in professional_roles:
                    role_obj, _ = ProfessionalRole.objects.get_or_create(name=role.get('name'))
                    lst_roles.append(role_obj)

                print('___SEARCH QUERY___')
                search_query = params.get('text')
                search_query_obj, _ = SearchQuery.objects.get_or_create(name=search_query)

                print('___EXPERIENCE___')
                experience = item.get('experience')
                experience_obj, _ = Experience.objects.get_or_create(code_name=experience.get('id'), name=experience.get('name'))

                print('___VACANCY___')
                vacancy_obj, _ = Vacancy.objects.get_or_create(
                    hh_vacancy_id=item.get('id'),
                    name=item.get('name'),
                    published_at=item.get('published_at'),
                    url=item.get('alternate_url'),
                    area=area_obj,
                    salary=salary_obj,
                    employer=employer_obj,
                    work_format=work_format_obj,
                    work_schedule=work_schedule_obj,
                    experience=experience_obj
                )
                vacancy_obj.search_query.add(search_query_obj)
                vacancy_obj.professional_roles.add(*lst_roles)
                
                # 
                vacancy_url = f"https://api.hh.ru/vacancies/{item.get('id')}"
                response_vacancy = requests.get(vacancy_url)
                detail_vacancy = response_vacancy.json()
                key_skills = detail_vacancy.get('key_skills')
                description = detail_vacancy.get('description')
                lst_skills = set()

                for skill in key_skills:
                    skill_obj, _ = Skill.objects.get_or_create(name=skill.get('name').lower())
                    lst_skills.add(skill_obj)

                description_lst = re.sub(r'[<>/().+,*]', ' ', description).split()
                description_set = set(description_lst)

                for i in description_set:
                    if i.lower() in skill_list:
                        skill_obj, _ = Skill.objects.get_or_create(name=i.lower())
                        lst_skills.add(skill_obj)


                vacancy_obj.skills.add(*lst_skills)


                print('Успешно')
            print('Успешно')
