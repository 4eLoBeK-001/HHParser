from django.shortcuts import get_object_or_404, render
from django.db.models import Count, Avg, F, FloatField, IntegerField, When, Case, Value
from django.db.models.functions import Round, Cast

from hh_app.models import Area, Employer, Experience, SearchQuery, Vacancy
from hh_parser.forms import SearchQueryForm

# Create your views here.

def home_page(request):

    context = {
    }
    return render(request, 'hh_app/home.html', context)


def searchquery_page(request):
    vacancies = None
    search_query = None
    if request.method == 'POST':
        form = SearchQueryForm(request.POST)
        if form.is_valid():
            cd_search_query = form.cleaned_data['name'].lower()
            search_query = get_object_or_404(SearchQuery, name=cd_search_query)
            vacancies = Vacancy.objects.filter(search_query=search_query)

    context = {
        'form': SearchQueryForm(),
        'vacancies': vacancies,
        'search_query': search_query
    }
    return render(request, 'hh_app/content.html', context)


def statistics(request, search_query):
    search_query = get_object_or_404(SearchQuery, name=search_query)
    count_vacancies = Vacancy.objects.filter(search_query=search_query, salary__currency='RUR').count()
    experiences = Experience.objects.all().order_by('id')
    result = (
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

    #  --- Топ-4 навыка ---
    raw_skills  = (
        Vacancy.objects
        .values('skills__name')
        .annotate(count=Count('id'))
        .filter(search_query=search_query, salary__currency='RUR')
        .order_by('-count')
        [:4]
    )

    skill_statistics = []
    for item in raw_skills:
        percent = (item["count"] / count_vacancies) * 100 if count_vacancies else 0
        skill_statistics.append({
            **item,
            "percent": round(percent, 1)
        })

    context = {
        'search_query': search_query,
        'experiences': experiences,
        'result': result,
        'skill_statistics': skill_statistics,
    }
    return render(request, 'hh_app/statistics.html', context)


def detail_statistics(request, search_query):
    search_query = get_object_or_404(SearchQuery, name=search_query)
    count_vacancies = (
        Vacancy.objects
        .filter(search_query=search_query, salary__currency='RUR')
        .values('employer__hh_employer_id')
        .aggregate(
            emp_count=Count('employer__hh_employer_id', distinct=True),
            vac_count=Count('id', distinct=True),
        )
    )
    print(count_vacancies)
    raw_skills  = (
        Vacancy.objects
        .values('skills__name')
        .annotate(count=Count('id'))
        .filter(search_query=search_query, salary__currency='RUR')
        .order_by('-count')
        [:15]
    )
    skill_statistics = []
    for item in raw_skills:
        percent = (item["count"] / count_vacancies.get('vac_count')) * 100 if count_vacancies.get('vac_count') else 0
        skill_statistics.append({
            **item,
            "percent": round(percent, 1)
        })
    
    work_format_lst = (
        Vacancy.objects
        .values("work_format__name")
        .annotate(count=Count('id'))
        .filter(search_query=search_query, salary__currency='RUR')
        .order_by('-count')
    )
    work_format_statistics = []
    for item in work_format_lst:
        percent = (item["count"] / count_vacancies.get('vac_count')) * 100 if count_vacancies.get('vac_count') else 0
        work_format_statistics.append({
            **item,
            "percent": round(percent, 1)
        })
    
    prof_roles = (
        Vacancy.objects
        .values('professional_roles__name')
        .annotate(count=Count('id'))
        .order_by('-count')
        .filter(search_query=search_query, salary__currency='RUR')
        [:3]
    ) 
    prof_roles_statistics = []
    for item in prof_roles:
        percent = (item["count"] / count_vacancies.get('vac_count')) * 100 if count_vacancies.get('vac_count') else 0
        prof_roles_statistics.append({
            **item,
            "percent": round(percent, 1)
        })
    experiences = Experience.objects.all().order_by('id')
    result = (
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
    context = {
        'search_query': search_query,
        'count_vacancies': count_vacancies,
        'skill_statistics': skill_statistics,
        'work_format_statistics': work_format_statistics,
        'prof_roles_statistics': prof_roles_statistics,
        'experiences': experiences,
        'result': result,
    }
    return render(request, 'hh_app/detail_statistics.html', context)


def cities_statistics(request):
    return render(request, 'hh_app/cities.html')


def city_statistics(request, area_name):
    area = get_object_or_404(Area, name=area_name)
    count_vacancies = Vacancy.objects.filter(area=area, salary__currency='RUR').count()
    experiences = Experience.objects.all().order_by('id')
    result = (
        Vacancy.objects
        .values('experience__code_name')
        .annotate(
            count=Count('id'), 
            salary_avg=Cast(
                Avg((F('salary__salary_from') + F('salary__salary_to')) / 2), # Средняя зп с учётом нижней и верхней границы
                output_field=IntegerField()
            ),
        )
        .filter(area=area, salary__currency='RUR')
        .order_by('experience__id')
    )
    area_stats = (
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
    raw_skills  = (
        Vacancy.objects
        .values('skills__name')
        .annotate(count=Count('id'))
        .filter(area=area, salary__currency='RUR')
        .order_by('-count')
        [:15]
    )
    skill_statistics = []
    for item in raw_skills:
        percent = (item["count"] / count_vacancies) * 100 if count_vacancies else 0
        skill_statistics.append({
            **item,
            "percent": round(percent, 1)
        })

    prof_roles = (
        Vacancy.objects
        .values('professional_roles__name')
        .annotate(count=Count('id'))
        .order_by('-count')
        .filter(area=area, salary__currency='RUR')
        [:3]
    ) 
    prof_roles_statistics = []
    for item in prof_roles:
        percent = (item["count"] / count_vacancies) * 100 if count_vacancies else 0
        prof_roles_statistics.append({
            **item,
            "percent": round(percent, 1)
        })
    context = {
        'area': area,
        'count_vacancies': count_vacancies,
        'experiences': experiences,
        'area_stats': area_stats,
        'result': result,
        'skill_statistics': skill_statistics,
        'prof_roles_statistics': prof_roles_statistics,
    }
    return render(request, 'hh_app/city.html', context)