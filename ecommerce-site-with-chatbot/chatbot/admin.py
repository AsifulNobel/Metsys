from django.contrib import admin
from .models import (Agent, BanglaRequests, BanglaResponses, EnglishRequests, EnglishResponses, ClassTag, Complaints, Feedbacks, Message, SessionTracker,
TagAccessHistory)

# Register your models here.
admin.site.register([Agent, BanglaRequests, BanglaResponses, EnglishRequests, EnglishResponses, ClassTag, Complaints, Feedbacks, Message, SessionTracker, TagAccessHistory])
