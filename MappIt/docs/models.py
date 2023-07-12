from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.SET('Deleted User'))

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('docs-questions-detail', kwargs={'pk': self.pk})



class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    date_creation = models.DateTimeField(default=timezone.now)
    icon = models.CharField(max_length=50, default=None)
    user = models.ForeignKey(User, on_delete=models.SET('Deleted User'))

    def __str__(self):
        return self.name

class DynamicModel(models.Model):
    # Definisci i campi dinamici del modello qui
    name = models.CharField(max_length=255, unique=True, verbose_name=_('Table Name'))

    def __str__(self):
        return self.name

class FieldModel(models.Model):
    dynamic_model = models.ForeignKey(DynamicModel, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, verbose_name=_('Field Name'))
    data_type = models.CharField(max_length=255, verbose_name=_('Data Type'))

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('dynamic_model', 'name')

class ValueModel(models.Model):
    dynamic_model = models.ForeignKey(DynamicModel, on_delete=models.CASCADE)
    code = models.CharField(max_length=255, unique=True, verbose_name=_('Mapping code'))
    name = models.ForeignKey(FieldModel, on_delete=models.CASCADE)
    value = models.CharField(max_length=255, verbose_name=_('Value'))

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('dynamic_model', 'name', 'code')