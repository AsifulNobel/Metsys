from django import forms
from .models import (ClassTag, BanglaRequests, EnglishRequests,
BanglaResponses, EnglishResponses, Agent)

class LoginForm(forms.Form):
    userName = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))

class EnglishTagForm(forms.Form):
    tag = forms.ModelChoiceField(queryset=ClassTag.objects.filter(agentId=Agent.objects.get(name='English Chowdhury')), empty_label=None, widget=forms.Select(attrs={'class':'form-control'}))

class BanglaTagForm(forms.Form):
    tag = forms.ModelChoiceField(queryset=ClassTag.objects.filter(agentId=Agent.objects.get(name='Bangla Chowdhury')), empty_label=None, widget=forms.Select(attrs={'class':'form-control'}))

class NewTagForm(forms.Form):
    new_tag = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    response = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))

class DurationForm(forms.Form):
    duration = forms.IntegerField(label='Duration(in minutes)', required=True, min_value=0, max_value=180)
