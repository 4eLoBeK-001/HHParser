from django import forms

from hh_app.models import Area, SearchQuery


class SearchQueryForm(forms.ModelForm):
    class Meta:
        model = SearchQuery
        fields = ('name',)
    
        labels = {
            'name': 'строка'
        }
        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input input-bordered w-full text-gray-700 text-lg bg-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-emerald-400', 'placeholder': 'Введите поисковое слово...'})
        }


class CitySearch(forms.ModelForm):
    class Meta:
        model = Area
        fields = ('name',)

