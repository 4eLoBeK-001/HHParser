from django.db.models import Count, Avg, F, IntegerField
from django.db.models.functions import Cast

from hh_app.models import Area, SearchQuery, Vacancy


def get_count_vacancies(
    *,
    search_query: SearchQuery | None = None,
    area: Area | None = None
) -> int:
    filters = {'salary__currency': 'RUR'}
    if search_query:
        filters['search_query'] = search_query
    if area:
        filters['area'] = area

    qs = Vacancy.objects.filter(**filters)

    return qs.count()


def get_avg_salary(*args):
    filters = {'salary__currency': 'RUR'}

    for arg in args:
        if isinstance(arg, SearchQuery):
            filters['search_query'] = arg
        elif isinstance(arg, Area):
            filters['area'] = arg
        else:
            raise ValueError(f'Неизвестный аргумент: {arg}')

    avg_salary = (
            Vacancy.objects
            .values('experience__code_name')
            .annotate(
                count=Count('id'), 
                salary_avg=Cast(
                    Avg((F('salary__salary_from') + F('salary__salary_to')) / 2),
                    output_field=IntegerField()
                ),
            )
            .filter(**filters)
            .order_by('experience__id')
        )    
    return avg_salary


def get_avg_salary_by_area(area):
    """Получение средней зарплаты всего города"""
    avg_salary = (
        Vacancy.objects
        .filter(area=area, salary__currency='RUR')
        .values("area__hh_area_id")
        .aggregate(
        count=Count('id'),
        sal_avg=Avg(
            (F("salary__salary_from") + F("salary__salary_to"))/2, 
            output_field=IntegerField())
        )
    )
    return avg_salary


def add_percentage(raw_skills, count_vacancies):
    skill_statistics = []
    for item in raw_skills:
        percent = (item["count"] / count_vacancies) * 100 if count_vacancies else 0
        skill_statistics.append({
            **item,
            "percent": round(percent, 1)
        })
    return skill_statistics


def get_raw_skill_counts(
        *,
        search_query: SearchQuery | None = None,
        area: Area | None = None
):
    """
    Возвращает queryset со статистикой навыков:
    [
        {"skill__name": "...", "count": 10},
        ...
    ]
    """
    filters = {'salary__currency': 'RUR'}

    if search_query is not None:
        filters['search_query'] = search_query

    if area is not None:
        filters['area'] = area
    
    qs = (
        Vacancy.objects
        .filter(**filters)
        .values('skills__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    return qs


def get_skill_statisticcs_by_search_query(
        search_query: SearchQuery,
        limit: int = 0
):

    raw_skills = get_raw_skill_counts(search_query=search_query)
    count_vacancies = get_count_vacancies(search_query=search_query)
    
    skill_stats = add_percentage(raw_skills, count_vacancies)
    return skill_stats[:limit]

def get_skill_statisticcs_by_area(
        area: Area,
        limit: int = 0
):

    raw_skills = get_raw_skill_counts(area=area)
    count_vacancies = get_count_vacancies(area=area)
    
    skill_stats = add_percentage(raw_skills, count_vacancies)
    return skill_stats[:limit]


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


def get_professional_roles_statistics(*args, count: int=0):
    if isinstance(args[-1], int):
        count = args[-1]
        args = args[:-1]

    filters = {'salary__currency': 'RUR'}
    prof_roles = (
        Vacancy.objects
        .values('professional_roles__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    if len(args) > 1:
        for arg in args:
            if isinstance(arg, SearchQuery):
                count_vacancies = get_count_vacancies(search_query=arg)
                filters['search_query'] = arg
                prof_roles_by_searchquery = prof_roles.filter(**filters)
                pfs = add_percentage(prof_roles_by_searchquery, count_vacancies)
            elif isinstance(arg, Area):
                count_vacancies = get_count_vacancies(area=arg)
                filters['area'] = arg
                prof_roles_by_area = prof_roles.filter(**filters)
                pfa = add_percentage(prof_roles_by_area, count_vacancies)
            else:
                raise ValueError(f'Неизвестный аргумент: {arg}')
        return [pfs[:count], pfa[:count]]
    else:
        for arg in args:
            if isinstance(arg, SearchQuery):
                count_vacancies = get_count_vacancies(search_query=arg)
                filters['search_query'] = arg
                prof_roles = prof_roles.filter(**filters)
                pf = add_percentage(prof_roles, count_vacancies)
            elif isinstance(arg, Area):
                count_vacancies = get_count_vacancies(area=arg)
                filters['area'] = arg
                prof_roles = prof_roles.filter(**filters)
                pf = add_percentage(prof_roles, count_vacancies)
            else:
                raise ValueError(f'Неизвестный аргумент: {arg}')
        return pf[:count]
