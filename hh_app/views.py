from django.shortcuts import get_object_or_404, render
from django.db.models import Count, Avg, F, FloatField, IntegerField, When, Case, Value
from django.db.models.functions import Round, Cast

from hh_app.models import Experience, SearchQuery, Vacancy
from hh_parser.forms import SearchQueryForm

# Create your views here.


def main_page(request):
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


def detailed_statistics(request, search_query):
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
    return render(request, 'hh_app/detailed_statistics.html', context)