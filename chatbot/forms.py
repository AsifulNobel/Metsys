from django import forms

class LoginForm(forms.Form):
    userName = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
