"""
    @author Nils Sohn, Nick Mattis
"""

from django import forms
from datetime import date

class ReservationRequestForm(forms.Form):
    start_date = forms.DateField(input_formats=["%m/%d/%y"])
    end_date = forms.DateField(input_formats=["%m/%d/%y"])

    def clean_start_date(self):
        start_date = self.cleaned_data['start_date']

        if start_date:
            if start_date < date.today():
                raise forms.ValidationError("The start date can't be in the past")
        return start_date

    def clean(self):
        cleaned_data = super(ReservationRequestForm, self).clean()
        end_date = cleaned_data.get("end_date")
        start_date = cleaned_data.get("start_date")

        if start_date:
            if end_date:
                if end_date < start_date:
                    raise forms.ValidationError("The end date can't be before the start date")
            else:
                end_date = None
        else:
            end_date = None

        return cleaned_data

class CreatePrivateShed(forms.Form):
    shed_name = forms.CharField()
    shed_address = forms.CharField()

class Search(forms.Form):
    search_term = forms.CharField()