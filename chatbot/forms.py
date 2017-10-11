from django import forms
from .models import (ClassTag, BanglaRequests, EnglishRequests,
BanglaResponses, EnglishResponses)

class LoginForm(forms.Form):
    userName = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))

class EnglishTagForm(forms.Form):
    tag_choices = [(x.tagName, x.tagName.upper()) for x in ClassTag.objects.raw('SELECT distinct c.id, c."tagName" from chatbot_classtag as c inner join chatbot_englishrequests as e on c.id=e.tag_id order by c."tagName" asc;')]
    tag = forms.CharField(widget=forms.Select(choices=tag_choices, attrs={'class':'form-control'}))

class BanglaTagForm(forms.Form):
    tag_choices = [(x.tagName, x.tagName.upper()) for x in ClassTag.objects.raw('SELECT distinct c.id, c."tagName" from chatbot_classtag as c inner join chatbot_banglarequests as e on c.id=e.tag_id order by c."tagName" asc;')]
    tag = forms.CharField(widget=forms.Select(choices=tag_choices, attrs={'class':'form-control'}))

class NewTagForm(forms.Form):
    new_tag = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    response = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
