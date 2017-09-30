from django.db import models
from django.utils import timezone

# Create your models here.
class ClassTag(models.Model):
    tagName = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.tagName

class EnglishRequests(models.Model):
    request = models.CharField(max_length=500, unique=True)
    tag = models.ForeignKey(ClassTag, on_delete=models.SET_NULL, null=True)

class BanglaRequests(models.Model):
    request = models.CharField(max_length=500, unique=True)
    tag = models.ForeignKey(ClassTag, on_delete=models.SET_NULL, null=True)

class EnglishResponses(models.Model):
    response = models.CharField(max_length=2000, unique=True)
    tag = models.ForeignKey(ClassTag, on_delete=models.SET_NULL, null=True)

class BanglaResponses(models.Model):
    response = models.CharField(max_length=2000, unique=True)
    tag = models.ForeignKey(ClassTag, on_delete=models.SET_NULL, null=True)

class ContextTag(models.Model):
    tagName = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.tagName

class Complaints(models.Model):
    request = models.CharField(max_length=500)
    response = models.CharField(max_length=2000)
    created = models.DateTimeField(auto_now_add=True)

class Feedbacks(models.Model):
    name = models.CharField(max_length=50, default='anonymous')
    comment = models.CharField(max_length=3000)
