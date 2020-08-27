from django import forms
from django.db.models import F
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    username = forms.CharField(max_length=20, widget=forms.TextInput(attrs={"autocomplete": "off"}))
    password = forms.CharField(max_length=20, widget=forms.PasswordInput(attrs={"autocomplete": "off"}))
