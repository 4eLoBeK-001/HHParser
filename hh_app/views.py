from django.shortcuts import get_object_or_404, render
from django.db.models import Count, Avg, F, FloatField, IntegerField
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
    experiences = Experience.objects.all()
    result = (
        Vacancy.objects
        .values('experience__code_name')
        .annotate(
            count=Count('id'), 
            salary_avg=Cast(
                Round(Avg((F('salary__salary_from')+F('salary__salary_to')) / 2), # Средняя зп с учётом нижней и верхней границы
                    output_field=FloatField()
                ), output_field=IntegerField()
            ),
        )
        .filter(search_query=search_query, salary__currency='RUR')
    )

    context = {
        'search_query': search_query,
        'experiences': experiences.order_by('code_name'),
        'result': result,
    }
    return render(request, 'hh_app/detailed_statistics.html', context)