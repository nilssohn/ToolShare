"""
    @author Nick Mattis
"""

from django import forms

class PasswordRecover(forms.Form):
    username = forms.EmailField()

class AnswersToQuestions(forms.Form):
    answer1 = forms.CharField(required=False)
    answer2 = forms.CharField(required=False)

class ShedAddress(forms.Form):
    address = forms.CharField(required=True)