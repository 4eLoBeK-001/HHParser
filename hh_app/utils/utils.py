import re
import requests
from typing import Any
from pprint import pprint

from hh_app.models import (Area, Salary, Employer, WorkFormat, WorkSchedule, 
                            ProfessionalRole, SearchQuery, Experience, Skill, Vacancy)
from hh_app.utils.session import HHSession
from hh_app.utils.skill_cache import SkillCache
from hh_app.utils.types import HHVacancy

skill_list = [
    # Языки программирования
    "python", "ООП", "javascript", 'js', "typescript", "java", "c", "c++", "c#", "go", "rust",
    "ruby", "php", "swift", "kotlin", "dart", "scala", "haskell", "elixir",
    "perl", "r", "matlab", "objective-c", "lua",

    # Фронтенд
    "html", "css", "sass", "less", "bootstrap", "tailwind", "jquery",
    "react", "next.js", "vue", "nuxt.js", "angular", "svelte", "ember.js",
    "webpack", "vite", "babel",

    # Бэкенд
    "django", "flask", "fastapi", "tornado",
    "spring", "spring boot", "hibernate",
    "express", "nest.js", "koa",
    "ruby on rails", "laravel", "symfony", "codeigniter",
    "asp.net", "gin", "fiber",

    # Базы данных
    "sql", "mysql", "postgresql", "sqlite", "mssql", "oracle", "mssql", "mariadb",
    "mongodb", "cassandra", "redis", "couchdb", "dynamodb", "neo4j", "elasticsearch",

    # DevOps / Контейнеризация
    "docker", "docker-compose", "kubernetes", "helm",
    "vagrant", "terraform", "ansible", "puppet", "chef",

    # Облака
    "aws", "gcp", "azure", "heroku", "digitalocean", "netlify", "vercel",

    # CI/CD
    "actions", "gitlab", "ci/cd", "jenkins", "travis ci", "circleci", "teamcity",

    # Контроль версий
    "git", "github", "svn", "mercurial",

    # Тестирование
    "pytest", "unittest", "selenium", "junit", "mocha", "chai", "jest", "cypress",
    "playwright", "karma", "rspec",

    # Data Science / ML / AI
    "numpy", "pandas", "scikit-learn", "tensorflow", "keras", "pytorch",
    "matplotlib", "seaborn", "plotly", "jupyter", "huggingface transformers",

    # Big Data
    "hadoop", "spark", "hive", "kafka", "flink",

    # Мобильная разработка
    "react native", "flutter", "swiftui", "jetpack compose", "ionic", "cordova",

    # Инструменты и другое
    "linux", "bash", "powershell", "vim", "emacs",
    "postman", "swagger", "graphql", "rest api", "grpc",
    "rabbitmq", "activemq", "zeromq", "nats",
    "nginx", "apache", "iis",
    "webpack", "rollup",
    "eslint", "prettier",
]


def create_area(item: HHVacancy) -> Area:
    area = item.get('area')
    area_obj, _ = Area.objects.get_or_create(hh_area_id=area.get('id'), name=area.get('name'))
    return area_obj


def create_salary(item: HHVacancy) -> Salary:
    salary = item.get('salary')
    salary_obj, _ = Salary.objects.get_or_create(
        salary_from=salary.get('from'), salary_to=salary.get('to'), 
        currency=salary.get('currency'), gross=salary.get('gross')
    )
    return salary_obj


def create_employer(item: HHVacancy) -> Employer:
    employer = item.get('employer')
    employer_obj, _ = Employer.objects.get_or_create(
        hh_employer_id=employer.get('id'), name=employer.get('name'), url=employer.get('alternate_url')
    )
    return employer_obj


def create_work_format(item: dict[str, Any]) -> WorkFormat:
    work_format = item.get('work_format')
    if not work_format:
        work_format_obj, _ = WorkFormat.objects.get_or_create(code_name=0, name='Не указано')
    else:
        work_format_obj, _ = WorkFormat.objects.get_or_create(code_name=work_format[0].get('id'), name=work_format[0].get('name'))

    return work_format_obj


def create_work_schedule(item: HHVacancy) -> WorkSchedule:
    work_schedule = item.get('work_schedule_by_days')
    working_hours = item.get('working_hours')[0].get('name')  or 'Не указано'
    if not work_schedule:
        work_schedule_obj, _ = WorkSchedule.objects.get_or_create(code_name=0, name='Не указано', working_hours='Не указано')
    else:
        work_schedule_obj, _ = WorkSchedule.objects.get_or_create(
            code_name=work_schedule[0].get('id'), name=work_schedule[0].get('name'), working_hours=working_hours
    )

    return work_schedule_obj


def create_proffesional_role(item: HHVacancy) -> list[ProfessionalRole]:
    professional_roles = item.get('professional_roles')
    if not professional_roles:
        role_obj, _ = ProfessionalRole.objects.get_or_create(name='Профессиональная роль не указана')
        return [role_obj]
    
    lst_roles = []
    for role in professional_roles:
        role_obj, _ = ProfessionalRole.objects.get_or_create(name=role.get('name'))
        lst_roles.append(role_obj)
    
    return lst_roles


def create_search_query(params: dict[str, str]) -> SearchQuery:
    search_query = params.get('text').lower()
    search_query_obj, _ = SearchQuery.objects.get_or_create(name=search_query)

    return search_query_obj


def create_experience(item: HHVacancy) -> Experience:
    experience = item.get('experience')
    experience_obj, _ = Experience.objects.get_or_create(code_name=experience.get('id'), name=experience.get('name'))

    return experience_obj


def create_skills(item: HHVacancy) -> set[Skill]:
    cache = SkillCache.get()
    session = HHSession.get()

    url = f"https://api.hh.ru/vacancies/{item['id']}"
    response = session.get(
        url,
        params={'fields': 'key_skills,description'},
        timeout=10
    ).json()
    
    key_skills = {
        skill['name'].lower() for skill in response.get('key_skills', [])
    }

    description = response.get('description', '')
    description_set = set(
        re.sub(r'[<>/().+,*]', ' ', description).lower().split()
    )

    skill_from_description = description_set.intersection(skill_list)
    
    total_skills = key_skills.union(skill_from_description)
    new_skills = total_skills - cache  # те, которых ещё нет в БД

    if new_skills:
        Skill.objects.bulk_create([Skill(name=name) for name in new_skills])
        SkillCache.add(new_skills)

    return set(Skill.objects.filter(name__in=total_skills))


def create_vacancy(item: HHVacancy, params: dict[str, str]) -> bool:
    employer = create_employer(item)
    area = create_area(item)
    salary = create_salary(item)
    work_format = create_work_format(item)
    work_schedule = create_work_schedule(item)
    experience = create_experience(item)
    proffesional_role = create_proffesional_role(item)
    search_query = create_search_query(params)
    skills = create_skills(item)

    vacancy_obj, created = Vacancy.objects.update_or_create(
        hh_vacancy_id=item.get('id'),
        defaults= {
            'name': item.get('name'),
            'published_at': item.get('published_at'),
            'url': item.get('alternate_url'),
            
            'employer': employer,
            'area': area,
            'salary': salary,
            'work_format': work_format,
            'work_schedule': work_schedule,
            'experience': experience,
        }
    )
    
    vacancy_obj.professional_roles.set(proffesional_role)
    vacancy_obj.search_query.add(search_query)
    vacancy_obj.skills.set(skills)

    return created