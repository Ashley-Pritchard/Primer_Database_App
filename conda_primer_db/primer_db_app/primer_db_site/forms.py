from django import forms
from django.db.models import F
from django.contrib.auth.models import User
import re
from .models import *

class LoginForm(forms.Form):
    username = forms.CharField(max_length=20, widget=forms.TextInput(attrs={"autocomplete": "off"}))
    password = forms.CharField(max_length=20, widget=forms.PasswordInput(attrs={"autocomplete": "off"}))

class IndexSearchForm(forms.Form):

    Amplicon_ID=forms.CharField(label=u"Amplicon ID", max_length=75, required=False)
    Chromosome=forms.CharField(label=u"Chromosome", max_length=2, required=False)
    Primer_Set=forms.ModelChoiceField(queryset = Primer_Set.objects.order_by("primer_set"), required=False, label=u"Primer Set")
    Gene=forms.CharField(label=u"Gene", max_length=75, required=False)
    Analysis_Type=forms.ModelChoiceField(queryset = Analysis_Type.objects.order_by("analysis_type"), required=False, label=u"Analysis Type")
    Alt_Name=forms.CharField(label=u"Alt Name", max_length=75, required=False)

    def clean(self):
        super(IndexSearchForm, self).clean()
        #regex that matches 1-22, X, Y or M ONLY (E.g X is fine, Y is fine, XY is not)
        Chr_regex="((^[1-9]$|^1[0-9]$|^2[0-2]$)|^X$|^Y$|^M$)"
        if self.cleaned_data["Chromosome"]!="":
            if not re.match(Chr_regex, self.cleaned_data["Chromosome"]):
                self.add_error("Chromosome", forms.ValidationError("Chromosome must be 1-22, X, Y or M"))

class AmpliconOrderForm(forms.Form):
    reason = forms.ChoiceField(label=u"Reason for Reorder", choices=[("Repeat order","Repeat order"),("New Gene/Version","New Gene/Version"),
                                                                      ("NGS Confirmation","NGS Confirmation"), ("Scientist - R&D","Scientist - R&D"),
                                                                      ("Other","Other")])

    # ReOrderedBy = forms.ModelChoiceField(label=u"Reordered By", queryset = Imported_By.objects.filter(status="current"))
