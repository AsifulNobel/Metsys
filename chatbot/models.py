from django.db import models
from django.utils import timezone


# Create your models here.
class ClassTag(models.Model):
    tagName = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.tagName

class EnglishRequests(models.Model):
    requestMessage = models.CharField(max_length=500)
    tag = models.ForeignKey(ClassTag, on_delete=models.SET_NULL, null=True)

class BanglaRequests(models.Model):
    requestMessage = models.CharField(max_length=500)
    tag = models.ForeignKey(ClassTag, on_delete=models.SET_NULL, null=True)

class EnglishResponses(models.Model):
    responseMessage = models.CharField(max_length=2000)
    tag = models.ForeignKey(ClassTag, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.responseMessage

class BanglaResponses(models.Model):
    responseMessage = models.CharField(max_length=2000)
    tag = models.ForeignKey(ClassTag, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.responseMessage

class Complaints(models.Model):
    requestMessage = models.CharField(max_length=500)
    responseMessage = models.CharField(max_length=2000)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Adds 6 hours to UTC time
        return "Complaint posted on: " + (self.created+timezone.timedelta(hours=6)).strftime("%Y-%b-%d %I:%M:%S %p")

class Feedbacks(models.Model):
    name = models.CharField(max_length=50, default='anonymous')
    comment = models.CharField(max_length=3000)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Feedback posted on: " + (self.created+timezone.timedelta(hours=6)).strftime("%Y-%b-%d %I:%M:%S %p")
