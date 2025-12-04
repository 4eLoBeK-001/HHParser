from django.shortcuts import render

from hh_parser.forms import SearchQueryForm

# Create your views here.


def main_page(request):
    if request.method == 'POST':
        form = SearchQueryForm(request.POST)
        if form.is_valid():
            search_query = form.cleaned_data['name']
    
    context = {
        'form': SearchQueryForm()
    }
    return render(request, 'hh_app/content.html', context)


