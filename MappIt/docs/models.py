from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

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
