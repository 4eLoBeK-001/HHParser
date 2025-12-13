from django.shortcuts import get_object_or_404, render
from django.db.models import Count, Avg, F, FloatField, IntegerField, When, Case, Value
from django.db.models.functions import Round, Cast

from hh_app.models import Area, Employer, Experience, SearchQuery, Vacancy
from hh_app.services.helpers import get_avg_salary, get_avg_salary_by_area, get_count_vacancies, get_professional_roles_statistics, get_skill_statisticcs, get_work_format_statistics
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
    experiences = Experience.objects.all().order_by('id')
    search_query = get_object_or_404(SearchQuery, name=search_query)
    count_vacancies = get_count_vacancies(search_query)
    avg_salary = get_avg_salary(search_query)
    skill_statistics = get_skill_statisticcs(search_query, 4)

    context = {
        'search_query': search_query,
        'experiences': experiences,
        'avg_salary': avg_salary,
        'skill_statistics': skill_statistics,
    }
    return render(request, 'hh_app/statistics.html', context)


def detail_statistics(request, search_query):
    search_query = get_object_or_404(SearchQuery, name=search_query)
    experiences = Experience.objects.all().order_by('id')
   
    count_vacancies = (
        Vacancy.objects
        .filter(search_query=search_query, salary__currency='RUR')
        .values('employer__hh_employer_id')
        .aggregate(
            emp_count=Count('employer__hh_employer_id', distinct=True),
            vac_count=Count('id', distinct=True),
        )
    )

    skill_statistics = get_skill_statisticcs(search_query, 15)
    work_format_statistics = get_work_format_statistics(search_query)
    prof_roles_statistics = get_professional_roles_statistics(search_query, 3)
    avg_salary = get_avg_salary(search_query)

    context = {
        'search_query': search_query,
        'count_vacancies': count_vacancies,
        'skill_statistics': skill_statistics,
        'work_format_statistics': work_format_statistics,
        'prof_roles_statistics': prof_roles_statistics,
        'experiences': experiences,
        'avg_salary': avg_salary,
    }
    return render(request, 'hh_app/detail_statistics.html', context)


def cities_statistics(request):
    return render(request, 'hh_app/cities.html')


def city_statistics(request, area_name):
    area = get_object_or_404(Area, name=area_name)
    count_vacancies = get_count_vacancies(area)
    experiences = Experience.objects.all().order_by('id')
    result = get_avg_salary(area)
    area_stats = get_avg_salary_by_area(area)
    skill_statistics = get_skill_statisticcs(area, count=15)
    prof_roles_statistics = get_professional_roles_statistics(area=area, count=3)
    distinct_emp = Employer.objects.filter(vacancies__area=area).distinct().count()
    
    context = {
        'area': area,
        'count_vacancies': count_vacancies,
        'experiences': experiences,
        'area_stats': area_stats,
        'result': result,
        'skill_statistics': skill_statistics,
        'prof_roles_statistics': prof_roles_statistics,
        'distinct_emp': distinct_emp,
    }
    return render(request, 'hh_app/city.html', context)


