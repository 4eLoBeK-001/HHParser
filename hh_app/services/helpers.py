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