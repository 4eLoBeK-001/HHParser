from django.shortcuts import get_object_or_404, render
from django.db.models import Count, Avg, F, FloatField, IntegerField, When, Case, Value
from django.db.models.functions import Round, Cast

from hh_app.models import Area, Employer, Experience, SearchQuery, Vacancy
from hh_app.services.helpers import get_avg_salary, get_count_vacancies, get_professional_roles_statistics, get_skill_statistics, get_work_format_statistics
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
    count_vacancies = get_count_vacancies(search_query=search_query)
    avg_salary = get_avg_salary(search_query=search_query)
    skill_statistics = get_skill_statistics(search_query=search_query, limit=4)

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
   
    count_vacancies_and_employers = (
        Vacancy.objects
        .filter(search_query=search_query, salary__currency='RUR')
        .values('employer__hh_employer_id')
        .aggregate(
            emp_count=Count('employer__hh_employer_id', distinct=True),
            vac_count=Count('id', distinct=True),
        )
    )

    skill_statistics = get_skill_statistics(search_query=search_query, limit=15)
    work_format_statistics = get_work_format_statistics(search_query)
    prof_roles_statistics = get_professional_roles_statistics(search_query=search_query, limit=3)
    avg_salary = get_avg_salary(search_query=search_query)

    context = {
        'search_query': search_query,
        'count_vacancies_and_employers': count_vacancies_and_employers,
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

    avg_salary_in_area = (
        Vacancy.objects
        .filter(area=area, salary__currency='RUR')
        .aggregate(
            avg_salary=Cast(Avg(
                Case(
                    When(
                        salary__salary_from__isnull=False,
                        salary__salary_to__isnull=False,
                        then=(F('salary__salary_from') + F('salary__salary_to')) / 2
                    ),
                    When(
                        salary__salary_from__isnull=False,
                        salary__salary_to__isnull=True,
                        then=F('salary__salary_from')
                    ),
                    When(
                        salary__salary_from__isnull=True,
                        salary__salary_to__isnull=False,
                        then=F('salary__salary_to')
                    ),
                    default=None,
                    output_field=FloatField(),
                )
            ), output_field=IntegerField())
        )
    )
    count_vacancies = get_count_vacancies(area=area)
    experiences = Experience.objects.all().order_by('id')
    avg_salary_by_area = get_avg_salary(area=area)
    skill_statistics = get_skill_statistics(area=area, limit=15)
    prof_roles_statistics = get_professional_roles_statistics(area=area, limit=3)
    distinct_emp = Employer.objects.filter(vacancies__area=area).distinct().count()
    
    context = {
        'area': area,
        'count_vacancies': count_vacancies,
        'experiences': experiences,
        'avg_salary_in_area': avg_salary_in_area,
        'avg_salary_by_area': avg_salary_by_area,
        'skill_statistics': skill_statistics,
        'prof_roles_statistics': prof_roles_statistics,
        'distinct_emp': distinct_emp,
    }
    return render(request, 'hh_app/city.html', context)


