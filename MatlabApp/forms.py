# MatlabApp/forms.py
from django import forms
from .models import Command

class CommandForm(forms.Form):
    command = forms.CharField(label='Command', max_length=100)


