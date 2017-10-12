from django.contrib import admin
from .models import (BanglaRequests, BanglaResponses, EnglishRequests, EnglishResponses, ClassTag, Complaints, Feedbacks)

# Register your models here.
admin.site.register([BanglaRequests, BanglaResponses, EnglishRequests, EnglishResponses, ClassTag, Complaints, Feedbacks])
