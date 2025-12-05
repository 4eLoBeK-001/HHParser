from django.shortcuts import get_object_or_404, render

from hh_app.models import SearchQuery, Vacancy
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
    return render(request, 'hh_app/detailed_statistics.html')