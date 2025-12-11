from django.shortcuts import get_object_or_404, render
from django.db.models import Count, Avg, F, FloatField, IntegerField, When, Case, Value
from django.db.models.functions import Round, Cast

from hh_app.models import Area, Employer, Experience, SearchQuery, Vacancy
from hh_parser.forms import SearchQueryForm


def get_count_vacancies(search_query):
    return Vacancy.objects.filter(search_query=search_query, salary__currency='RUR').count()


def get_avg_salary(search_query):
    avg_salary = (
        Vacancy.objects
        .values('experience__code_name')
        .annotate(
            count=Count('id'), 
            salary_avg=Cast(
                Avg((F('salary__salary_from') + F('salary__salary_to')) / 2), # Средняя зп с учётом нижней и верхней границы
                output_field=IntegerField()
            ),
        )
        .filter(search_query=search_query, salary__currency='RUR')
        .order_by('experience__id')
    )
    return avg_salary


def get_skill_statisticcs(search_query, count: int):
    count_vacancies = get_count_vacancies(search_query)

    raw_skills  = (
        Vacancy.objects
        .values('skills__name')
        .annotate(count=Count('id'))
        .filter(search_query=search_query, salary__currency='RUR')
        .order_by('-count')
        [:count]
    )

    skill_statistics = []
    for item in raw_skills:
        percent = (item["count"] / count_vacancies) * 100 if count_vacancies else 0
        skill_statistics.append({
            **item,
            "percent": round(percent, 1)
        })
    
    return skill_statistics

def get_work_format_statistics(search_query):
    count_vacancies = get_count_vacancies(search_query)

    work_format_lst = (
        Vacancy.objects
        .values("work_format__name")
        .annotate(count=Count('id'))
        .filter(search_query=search_query, salary__currency='RUR')
        .order_by('-count')
    )
    work_format_statistics = []
    for item in work_format_lst:
        percent = (item["count"] / count_vacancies) * 100 if count_vacancies else 0
        work_format_statistics.append({
            **item,
            "percent": round(percent, 1)
        })
    
    return work_format_statistics


def get_professional_roles_statistics(search_query, count):
    count_vacancies = get_count_vacancies(search_query)

    prof_roles = (
        Vacancy.objects
        .values('professional_roles__name')
        .annotate(count=Count('id'))
        .order_by('-count')
        .filter(search_query=search_query, salary__currency='RUR')
        [:count]
    ) 
    professional_roles_statistics = []
    for item in prof_roles:
        percent = (item["count"] / count_vacancies) * 100 if count_vacancies else 0
        professional_roles_statistics.append({
            **item,
            "percent": round(percent, 1)
        })
    
    return professional_roles_statistics