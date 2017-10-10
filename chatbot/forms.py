from django import forms
from .models import (ClassTag, BanglaRequests, EnglishRequests,
BanglaResponses, EnglishResponses)

class LoginForm(forms.Form):
    userName = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class EnglishTagForm(forms.Form):
    tag_choices = [(x.tagName, x.tagName.upper()) for x in ClassTag.objects.raw('SELECT distinct c.id, c."tagName" from chatbot_classtag as c inner join chatbot_englishrequests as e on c.id=e.tag_id order by c."tagName" asc;')]
    tag = forms.CharField(widget=forms.Select(choices=tag_choices))

class BanglaTagForm(forms.Form):
    tag_choices = [(x.tagName, x.tagName.upper()) for x in ClassTag.objects.raw('SELECT distinct c.id, c."tagName" from chatbot_classtag as c inner join chatbot_banglarequests as e on c.id=e.tag_id order by c."tagName" asc;')]
    tag = forms.CharField(widget=forms.Select(choices=tag_choices))

class NewTagForm(forms.Form):
    new_tag = forms.CharField()
    response = forms.CharField()
