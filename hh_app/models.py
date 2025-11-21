from django.db import models

# Create your models here.


class Area(models.Model):
    hh_area_id = models.IntegerField(help_text='Номер региона')
    name = models.CharField(max_length=100, help_text='Название региона')


class Salary(models.Model):
    salary_from = models.IntegerField()
    salary_to = models.IntegerField()
    currency = models.CharField(max_length=15, help_text='Курс')
    gross = models.BooleanField(help_text='ЗП указана до либо после вычета налогов')


class Employer(models.Model):
    hh_employer_id = models.IntegerField()
    name = models.CharField(max_length=150, help_text='Название работодателя')
    url = models.URLField(help_text='Ссылка на работодателя')


class WorkFormat(models.Model):
    code_name = models.CharField(max_length=25)
    name = models.CharField(max_length=50, help_text='Формат работы')


class WorkSchedule(models.Model):
    code_name = models.CharField(max_length=25)
    name = models.CharField(max_length=50, help_text='График работы')
    working_hours = models.CharField(max_length=25)


class ProfessionalRole(models.Model):
    name = models.CharField(max_length=250, help_text='Профессиональная роль')


class SearchQuery(models.Model):
    name = models.CharField(max_length=250, help_text='Запрос по которому была найдена вакансия')


class Experience(models.Model):
    code_name = models.CharField(max_length=25)
    name = models.CharField(max_length=50, help_text='Опыт работы')


class Skill(models.Model):
    name = models.CharField(max_length=50, help_text='Навыки')


class Vacancy(models.Model):
    hh_vacancy_id = models.IntegerField(help_text='id вакансии у hh.ru')
    name = models.CharField(max_length=255, help_text='Заголовок вакансии')
    published_at = models.DateTimeField(help_text='Когда вакансия была опубликована в hh.ru')
    fetched_at = models.DateTimeField(auto_now_add=True, help_text='Когда запись появилась в БД')
    url = models.URLField(help_text='Ссылка на вакансию')

    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    salary = models.ForeignKey(Salary, on_delete=models.CASCADE)
    work_format = models.ForeignKey(WorkFormat, on_delete=models.CASCADE)
    work_schedule = models.ForeignKey(WorkSchedule, on_delete=models.CASCADE)
    experience = models.ForeignKey(Experience, on_delete=models.CASCADE)

    search_query = models.ManyToManyField(SearchQuery)
    professional_roles = models.ManyToManyField(ProfessionalRole)
    skills = models.ManyToManyField(Skill)