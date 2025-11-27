from django.contrib import admin

from hh_app.models import (Area, Salary, Employer, WorkFormat, WorkSchedule, 
                            ProfessionalRole, SearchQuery, Experience, Skill, Vacancy)
# Register your models here.


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('hh_area_id', 'name')
    fields = ('hh_area_id', 'name')


@admin.register(Salary)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('salary_from', 'salary_to', 'currency', 'gross')
    fields = ('salary_from', 'salary_to', 'currency', 'gross')


@admin.register(Employer)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('hh_employer_id', 'name', 'url')
    fields = ('hh_employer_id', 'name', 'url')


@admin.register(WorkFormat)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('code_name', 'name')
    fields = ('code_name', 'name')


@admin.register(WorkSchedule)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('code_name', 'name', 'working_hours')
    fields = ('code_name', 'name', 'working_hours')


@admin.register(ProfessionalRole)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('name',)
    fields = ('name',)


@admin.register(SearchQuery)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('name',)
    fields = ('name',)


@admin.register(Experience)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('code_name', 'name')
    fields = ('code_name', 'name')


@admin.register(Skill)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('name',)
    fields = ('name',)


@admin.register(Vacancy)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('hh_vacancy_id', 'name', 'published_at', 'employer', 'area', 'salary', 'work_format', 'experience')
    fields = ('hh_vacancy_id', 'name', 'published_at', 'url', 'employer', 'area', 'salary', 'work_format', 'experience', 'search_query', 'professional_roles', 'skills')
    readonly_fields = ('published_at', 'fetched_at',)
