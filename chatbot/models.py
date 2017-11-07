from django.db import models
from django.utils import timezone

class Agent(models.Model):
    """Stores Chatbot identification properties"""
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class ClassTag(models.Model):
    tagName = models.CharField(max_length=255)
    agentId = models.ForeignKey(Agent, on_delete=models.CASCADE, null=True)
    errorCount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.tagName

class ContextMethod(models.Model):
    methodName = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.methodName

class Context(models.Model):
    contextClass = models.ForeignKey(ClassTag, related_name='others', on_delete=models.CASCADE, null=True)
    contextMethod = models.ForeignKey(ContextMethod, on_delete=models.CASCADE, null=True)
    contextParent = models.ForeignKey(ClassTag, related_name='parent', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return "Tag={}, Method={}".format(self.contextClass, self.contextMethod)

class EnglishRequests(models.Model):
    requestMessage = models.CharField(max_length=500)
    tag = models.ForeignKey(ClassTag, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return "Tag={}, Message={:.10}".format(self.tag, self.requestMessage)

class BanglaRequests(models.Model):
    requestMessage = models.CharField(max_length=500)
    tag = models.ForeignKey(ClassTag, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return "Tag={}, Message={:.10}".format(self.tag, self.requestMessage)

class EnglishResponses(models.Model):
    responseMessage = models.CharField(max_length=2000)
    tag = models.ForeignKey(ClassTag, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.responseMessage

class BanglaResponses(models.Model):
    responseMessage = models.CharField(max_length=2000)
    tag = models.ForeignKey(ClassTag, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.responseMessage


class Feedbacks(models.Model):
    name = models.CharField(max_length=50, default='anonymous')
    comment = models.CharField(max_length=3000)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Feedback posted on: " + (self.created+timezone.timedelta(hours=6)).strftime("%Y-%b-%d %I:%M:%S %p")

class SessionTracker(models.Model):
    text_id = models.CharField(max_length=32, null=False, blank=False)

    def __str__(self):
        return "ID={}".format(self.text_id)

class Message(models.Model):
    text = models.CharField(max_length=1000, null=False, blank=False)
    session_id = models.ForeignKey(SessionTracker, on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}, Created on={}".format(self.session_id, self.timestamp)

class TagAccessHistory(models.Model):
    session_id = models.ForeignKey(SessionTracker, on_delete=models.CASCADE, null=True)
    tag = models.ForeignKey(ClassTag, on_delete=models.CASCADE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}, Created on={}".format(self.session_id, self.timestamp)


class Complaints(models.Model):
    requestMessage = models.CharField(max_length=500)
    responseMessage = models.CharField(max_length=2000)
    session_id = models.ForeignKey(SessionTracker, on_delete=models.CASCADE, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Adds 6 hours to UTC time
        return "Complaint posted on: " + (self.created+timezone.timedelta(hours=6)).strftime("%Y-%b-%d %I:%M:%S %p")
