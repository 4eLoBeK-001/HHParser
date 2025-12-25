from datetime import timedelta

from django.utils import timezone
from django.shortcuts import get_object_or_404, render
from django.db.models import Count, Avg, F, Q, IntegerField, When, Case, Value, Min, Max
from django.db.models.functions import Round, Cast

from hh_app.models import Area, Employer, Experience, ProfessionalRole, SearchQuery, Vacancy, WorkFormat, WorkSchedule
from hh_app.services.helpers import add_percentage, avg_salary_expression, get_avg_salary, get_count_vacancies, get_professional_roles_statistics, get_skill_statistics, get_work_format_statistics
from hh_app.forms import CitySearch, SearchQueryForm

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
    areas = Area.objects.values('name').annotate(count=Count('vacancies')).order_by('-count')[:3]
    count_all_vacancies = Vacancy.objects.all().count()
    stat = add_percentage(areas, count_all_vacancies)

    form = CitySearch()
    cities = None
    if request.method == 'POST':
        form = CitySearch(request.POST)
        if form.is_valid():
            cd = form.cleaned_data['name']
            cities = (
                Area.objects
                .annotate(
                    vac_count=Count('vacancies'), 
                    avg_salary=Cast(Avg(avg_salary_expression())
                    ), output_field=IntegerField()
                ).filter(name__icontains=cd)
            )
            
    context = {
        'form': form,
        'cities': cities,
        'top_three_cities': stat,
    }
    return render(request, 'hh_app/cities.html', context)


def city_statistics(request, area_name):
    area = get_object_or_404(Area, name=area_name)

    avg_salary_in_area = (
        Vacancy.objects
        .filter(area=area, salary__currency='RUR')
        .aggregate(
            avg_salary=Cast(Avg(avg_salary_expression()), output_field=IntegerField()
            )
        )
    )
    count_vacancies = get_count_vacancies(area=area)
    experiences = Experience.objects.all().order_by('id')
    avg_salary_by_area = get_avg_salary(area=area)
    skill_statistics = get_skill_statistics(area=area, limit=15)
    prof_roles_statistics = get_professional_roles_statistics(area=area, limit=3)
    distinct_emp = Employer.objects.filter(vacancies__area=area).distinct().count()


    month_ago = timezone.now() - timedelta(days=30)
    ws = WorkSchedule.objects.filter(working_hours__contains='8')
    max_and_min_salary = (
        Vacancy.objects
        .filter(
            area=area,
            salary__currency='RUR',
            published_at__gte=month_ago, 
            work_schedule__in=ws
        )
        .values("area__hh_area_id")
        .aggregate(min_sal=Min('salary__salary_from'), max_sal=Max('salary__salary_to'))
    )

    
    context = {
        'area': area,
        'count_vacancies': count_vacancies,
        'experiences': experiences,
        'avg_salary_in_area': avg_salary_in_area,
        'avg_salary_by_area': avg_salary_by_area,
        'skill_statistics': skill_statistics,
        'prof_roles_statistics': prof_roles_statistics,
        'distinct_emp': distinct_emp,
        'max_and_min_salary': max_and_min_salary,
    }
    return render(request, 'hh_app/city.html', context)


def employers_list(request):
    employers = (
        Employer.objects
        .annotate(
            count_vac=Count('vacancies', distinct=True),
            avg_salary=Cast(
                Avg(avg_salary_expression(prefix='vacancies__salary')), output_field=IntegerField()
                )
            )
        ).order_by('-count_vac')
    context = {
        'employers_count': employers.count(),
        'employers': employers[:75],
    }
    return render(request, 'hh_app/employers.html', context)


def employer_detailed(request, hh_employer_id):
    vacancies = Vacancy.objects.filter(employer__hh_employer_id=hh_employer_id).order_by('published_at')
    employer = get_object_or_404(
        Employer.objects
        .annotate(
            count_vac=Count('vacancies', distinct=True),
            cities_count=Count('vacancies__area', distinct=True),
            prof_roles_count=Count('vacancies__professional_roles', distinct=True),
            avg_salary=Cast(
                Avg(avg_salary_expression(prefix='vacancies__salary')), output_field=IntegerField()
                )
            ).order_by('-count_vac'),
            hh_employer_id=hh_employer_id
        )
        
    context = {
        'employer': employer,
        'vacancies': vacancies,
    }
    return render(request, 'hh_app/employer.html', context)


def custom_filters(request):
    statistics = None
    vacancies = None
    experiences = Experience.objects.all()
    work_formats = WorkFormat.objects.all()

    field_mapping = {
        # Ключём служит поле для фильта в .filter
        # Значением служит то достаётся через request.POST
        'area__name': 'area_name',
        'employer__name': 'employer_name',
        'professional_roles__name': 'role_name',
        'experience_id': 'experience',
        'work_format_id': 'work_format',
        'salary__salary_from__gte': 'salary_from',  # Для ЗП проверка на больше чем и меньше чем
        'salary__salary_to__lte': 'salary_to',
    }

    filters = Q()

    if request.method == 'POST':
        for model_field, form_field in field_mapping.items():
            value = request.POST.get(form_field)
            if value:
                if 'salary' in model_field:
                    value = int(value)
                filters &= Q(**{model_field: value})

        vacancies = Vacancy.objects.filter(filters).distinct()

    context = {
        'experiences': experiences,
        'work_formats': work_formats,
        'statistics': statistics,
        'vacancies': vacancies,
    }
    return render(request, 'hh_app/custom_filters.html', context)


def area_autocomplete(request):
    query = request.GET.get('area_name', '').strip()

    areas = (
        Area.objects
        .filter(name__icontains=query)
        .order_by('name')[:10]
    )
    context = {
        'areas': areas
    }
    return render(request, 'hh_app/includes/area_autocomplete.html', context)


def employer_autocomplete(request):
    query = request.GET.get('employer_name', '').strip()

    employers = Employer.objects.none()
    if len(query) >= 2:
        employers = (
            Employer.objects
            .filter(name__icontains=query)
            .order_by('name')[:10]
        )
    context = {
        'employers': employers
    }
    return render(request, 'hh_app/includes/employer_autocomplete.html', context)


def role_autocomplete(request):
    query = request.GET.get('role_name', '').strip()

    roles = ProfessionalRole.objects.none()
    if len(query) >= 2:
        roles = (
            ProfessionalRole.objects
            .filter(name__icontains=query)
            .order_by('name')[:10]
        )

    context = {
        'roles': roles
    }
    return render(request, 'hh_app/includes/role_autocomplete.html', context)
