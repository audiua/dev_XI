from django.db import models

class DateTimeModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Counsil(DateTimeModel):
    """
    Модель совета(Рады)
    """
    title = models.CharField(max_length=255)

class CounsilSession(DateTimeModel):
    """
    Модель сессии рады
    Каждая сессия относится краде
    """
    counsil = models.ForeignKey(Counsil, related_name="sessions")
    from_date = models.DateField()
    number = models.CharField(max_length=55)
    title = models.CharField(max_length=255)
    voting_result_file = models.CharField(max_length=255)

class Law(DateTimeModel):
    """
    Модель законопроекта
    Каждый законопроект относится к сессии
    В сессии могут повторятся законы, для идентификации добавляем html файл(страницу в пдф файле)
    """
    session = models.ForeignKey(CounsilSession, related_name='laws')
    text = models.TextField()
    voting_result = models.CharField(max_length=255)
    resolution = models.CharField(max_length=255)
    voting_number = models.CharField(max_length=255)
    law_file_name = models.CharField(max_length=255, blank=True, null=True)

class Deputy(DateTimeModel):
    """
    Модель депутата
    Каждый депутат относится к раде
    """
    name = models.CharField(max_length=255)
    counsil = models.ForeignKey(Counsil, related_name="deputies")

class LawVoting(DateTimeModel):
    """
    Модель для отображения голосования депутатами 
    по каждому законопроекту и по каждому депутату
    """
    law = models.ForeignKey(Law, related_name='name_voting')
    deputy = models.ForeignKey(Deputy, related_name='law_voting')
    vote = models.CharField(max_length=255)






