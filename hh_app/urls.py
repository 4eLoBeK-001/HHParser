from django.urls import path

from hh_app import views


app_name = 'hh_app'

urlpatterns = [
    path('home/', views.main_page)
]