from django.urls import path

from hh_app import views


app_name = 'hh_app'

urlpatterns = [
    path('home/', views.home_page),
    path('cities/', views.cities_statistics, name='cities_statistics'),
    path('city/<str:area_name>/detail/', views.city_statistics, name='city_statistics'),
    path('query/', views.searchquery_page, name='searchquery_page'),
    path('vacancies/<str:search_query>/', views.statistics, name='statistics'),
    path('vacancies/<str:search_query>/detail/', views.detail_statistics, name='detail_statistics'),

    path('employers/', views.employers_list, name='employers_list'),
    path('employer/<hh_employer_id>/', views.employer_detailed, name='employer_detailed'),

    path('custom/', views.custom_filters, name='custom_filters'),
    path('htmx/areas/', views.area_autocomplete, name='area_autocomplete'),
    path('htmx/employers/', views.employer_autocomplete, name='employer_autocomplete'),
]