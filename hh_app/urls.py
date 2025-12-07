from django.urls import path

from hh_app import views


app_name = 'hh_app'

urlpatterns = [
    path('home/', views.main_page),
    path('vacancies/<str:search_query>/', views.statistics, name='statistics'),
    path('vacancies/<str:search_query>/detail/', views.detail_statistics, name='detail_statistics'),
]