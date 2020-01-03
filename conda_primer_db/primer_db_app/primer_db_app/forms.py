#-*- coding: utf-8 -*-
from django import forms 

class SearchForm(forms.Form):
	Gene = forms.CharField(max_length = 50)
