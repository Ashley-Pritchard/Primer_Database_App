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
    reason=forms.ModelChoiceField(queryset=Order_reason.objects.all(), label=u"Reason for Order")
class NewPrimerOrderForm(forms.Form):
    number=forms.IntegerField(min_value=1, label="How many primers would you like to order for your amplicon set?")

class OrderFormAmplicon(forms.Form):
    analysis_type=forms.ModelChoiceField(queryset=Analysis_Type.objects.all(), label=u"Analysis Type")
    gene=forms.CharField(label=u"Gene", max_length=75)
    chromosome=forms.CharField(label=u"Chromosome", max_length=2)
    exon=forms.IntegerField(label=u"Exon", required=False)
    primer_set=forms.ModelChoiceField(queryset=Primer_Set.objects.all(), label=u"Primer Set", required=False)


    def clean(self):
        super(OrderFormAmplicon, self).clean()
        #regex that matches 1-22, X, Y or M ONLY (E.g X is fine, Y is fine, XY is not)
        Chr_regex="((^[1-9]$|^1[0-9]$|^2[0-2]$)|^X$|^Y$|^M$)"
        if self.cleaned_data["chromosome"]!="":
            if not re.match(Chr_regex, self.cleaned_data["chromosome"]):
                self.add_error("chromosome", forms.ValidationError("Chromosome must be 1-22, X, Y or M"))
        if self.cleaned_data["primer_set"] is None and ((self.cleaned_data["analysis_type"].analysis_type=="Sanger") or (self.cleaned_data["analysis_type"].analysis_type=="NGS")):
            self.add_error("primer_set",f"Primer Set must be selected for {self.cleaned_data['analysis_type'].analysis_type}")
        if self.cleaned_data["analysis_type"].analysis_type!="NGS" and self.cleaned_data["analysis_type"] is not None and self.cleaned_data["exon"] is None:
            self.add_error("exon", f"Exon must be selected for analysis type {self.cleaned_data['analysis_type'].analysis_type}")


class OrderFormPrimer(forms.Form):
    sequence=forms.CharField(max_length=150, label=u"Sequence")
    direction=forms.ModelChoiceField(queryset=Direction.objects.all(), label=u"Direction")
    start=forms.IntegerField(label=u"Genomic Location Start", required=False)
    end=forms.IntegerField(label=u"Genomic Location End", required=False)
    m13=forms.ChoiceField(label=u"M13 Tag (for R/F primers) Note: auto-added for Sanger", choices=[("YES","YES"),("NO","NO")])
    prime3=forms.ModelChoiceField(queryset=Modification.objects.all(),label=u"3' Modification", required=False)
    prime5=forms.ModelChoiceField(queryset=Modification.objects.all(),label=u"5' Modification", required=False)
    ngs_number=forms.CharField(label=u"NGS Audit Number", required=False, max_length=25)
    alt_name=forms.CharField(label=u"Alternative Name", required=False, max_length=255)
    comments=forms.CharField(label=u"Comments", required=False, max_length=255)
    reason=forms.ModelChoiceField(queryset=Order_reason.objects.all(), label=u"Reason for Order")

    def clean(self):
        super(OrderFormPrimer, self).clean()
        seq_regex="^[ATCG]+$"
        if not re.match(seq_regex, self.cleaned_data["sequence"]):
            self.add_error("sequence", "Sequence contains invalid characters. Sequence must only contain A, T, C or G")
