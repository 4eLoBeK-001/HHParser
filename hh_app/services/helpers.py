from django.db.models import F, Value, Case, When, FloatField, IntegerField, Avg, Count
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

def _aggregate_avg_salary(queryset):
    """
    функция для агрегации средней зарплаты по опыту.
    Возвращает список словарей с полями:
    - experience__code_name:     опыт работы
    - count:                     кол-во вакансий на данный опыт работы
    - salary_avg:                средняя ЗП на каждый опыт работы
    """
    # подсчёт для средней зарплаты с учетом NULL
    salary_expr = Case(
        # оба значения указаны
        When(salary__salary_from__isnull=False, salary__salary_to__isnull=False,
             then=(F('salary__salary_from') + F('salary__salary_to')) / 2),
        # только salary_from
        When(salary__salary_from__isnull=False, salary__salary_to__isnull=True,
             then=F('salary__salary_from')),
        # только salary_to
        When(salary__salary_from__isnull=True, salary__salary_to__isnull=False,
             then=F('salary__salary_to')),
        # если оба NULL то оно не учитывается
        default=None,
        output_field=FloatField()
    )

    return (
        queryset
        .values('experience__code_name')
        .annotate(
            count=Count('id'),
            salary_avg=Cast(Avg(salary_expr), IntegerField())
        )
        .order_by('experience__id')
    )


def get_avg_salary(
    *,
    search_query: SearchQuery | None = None,      
    area: Area | None = None,      
):
    qs = Vacancy.objects.filter(salary__currency='RUR')

    if search_query:
        qs = qs.filter(search_query=search_query)
    if area:
        qs = qs.filter(area=area)

    return _aggregate_avg_salary(qs)


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


def get_skill_statistics(
    *,
    search_query: SearchQuery | None = None,
    area: Area | None = None,
    limit: int = 0
):
    raw_skills = get_raw_skill_counts(
        search_query=search_query,
        area=area
    )
    count_vacancies = get_count_vacancies(
        search_query=search_query,
        area=area
    )
    skill_stats = add_percentage(raw_skills, count_vacancies)

    return skill_stats[:limit]



def get_work_format_statistics(search_query):
    count_vacancies = get_count_vacancies(search_query=search_query)

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


def get_raw_professional_role_counts(
    *,
    search_query: SearchQuery | None = None,
    area: Area | None = None,
):
    filters = {'salary__currency': 'RUR'}
    
    if search_query is not None:
        filters['search_query'] = search_query

    if area is not None:
        filters['area'] = area

    qs = (
        Vacancy.objects
        .filter(**filters)
        .values('professional_roles__name')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    return qs

def get_professional_roles_statistics(
        *,
        search_query: SearchQuery | None = None,
        area: Area | None = None,
        limit: int=0
):
    if search_query is None and area is None:
        raise ValueError("Хотя-бы один аргумент search_query или area должен быть передан")

    count_vacancies = get_count_vacancies(
        search_query=search_query,
        area=area,
    )

    professional_role_counts = get_raw_professional_role_counts(
        search_query=search_query,
        area=area,
    )
    professional_role_statistics = add_percentage(professional_role_counts, count_vacancies)

    return professional_role_statistics[:limit]


def avg_salary_expression(prefix='salary'):
    return Case(
        When(
            **{
                f'{prefix}__salary_from__isnull': False,
                f'{prefix}__salary_to__isnull': False,
            },
            then=(F(f'{prefix}__salary_from') + F(f'{prefix}__salary_to')) / 2
        ),
        When(
            **{
                f'{prefix}__salary_from__isnull': False,
                f'{prefix}__salary_to__isnull': True,
            },
            then=F(f'{prefix}__salary_from')
        ),
        When(
            **{
                f'{prefix}__salary_from__isnull': True,
                f'{prefix}__salary_to__isnull': False,
            },
            then=F(f'{prefix}__salary_to')
        ),
        output_field=FloatField(),
    )
