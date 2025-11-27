from django.db import models

# Create your models here.


class Area(models.Model):
    hh_area_id = models.IntegerField(help_text='Номер региона')
    name = models.CharField(max_length=100, help_text='Название региона')

    def __str__(self):
        return self.name


class Salary(models.Model):
    salary_from = models.IntegerField(null=True)
    salary_to = models.IntegerField(null=True)
    currency = models.CharField(max_length=15, help_text='Курс')
    gross = models.BooleanField(help_text='ЗП указана до либо после вычета налогов')

    def __str__(self):
        if self.salary_from is None:
            return f'зарплата до {self.salary_to}'
        elif self.salary_to is None:
            return f'зарплата от {self.salary_from}'
        return f'зарплата от {self.salary_from} до {self.salary_to}'

class Employer(models.Model):
    hh_employer_id = models.IntegerField()
    name = models.CharField(max_length=150, help_text='Название работодателя')
    url = models.URLField(help_text='Ссылка на работодателя')

    def __str__(self):
        return self.name


class WorkFormat(models.Model):
    code_name = models.CharField(max_length=25)
    name = models.CharField(max_length=50, help_text='Формат работы')

    def __str__(self):
        return self.name


class WorkSchedule(models.Model):
    code_name = models.CharField(max_length=25)
    name = models.CharField(max_length=50, help_text='График работы')
    working_hours = models.CharField(max_length=25)

    def __str__(self):
        return self.name


class ProfessionalRole(models.Model):
    name = models.CharField(max_length=250, help_text='Профессиональная роль')

    def __str__(self):
        return self.name


class SearchQuery(models.Model):
    name = models.CharField(max_length=250, help_text='Запрос по которому была найдена вакансия')

    def __str__(self):
        return self.name


class Experience(models.Model):
    code_name = models.CharField(max_length=25)
    name = models.CharField(max_length=50, help_text='Опыт работы')

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=50, help_text='Навыки')

    def __str__(self):
        return self.name


class Vacancy(models.Model):
    hh_vacancy_id = models.IntegerField(help_text='id вакансии у hh.ru')
    name = models.CharField(max_length=255, help_text='Заголовок вакансии')
    published_at = models.DateTimeField(help_text='Когда вакансия была опубликована в hh.ru')
    fetched_at = models.DateTimeField(auto_now_add=True, help_text='Когда запись появилась в БД')
    url = models.URLField(help_text='Ссылка на вакансию')

    employer = models.ForeignKey(Employer, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True, blank=True)
    salary = models.ForeignKey(Salary, on_delete=models.CASCADE, null=True, blank=True)
    work_format = models.ForeignKey(WorkFormat, on_delete=models.CASCADE)
    work_schedule = models.ForeignKey(WorkSchedule, on_delete=models.CASCADE)
    experience = models.ForeignKey(Experience, on_delete=models.CASCADE)

    search_query = models.ManyToManyField(SearchQuery)
    professional_roles = models.ManyToManyField(ProfessionalRole)
    skills = models.ManyToManyField(Skill)


    def __str__(self):
        return self.name