"""
    @authors Tina Howard, Grant Gadomski, Nick Mattis, Nils Sohn
"""

from django import forms

from registration.models import Tool, Reservation
from datetime import date

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput, max_length = 16, min_length = 6)

    widgets = {
                'password': forms.PasswordInput(),
              }

'''
Basic form class for the User registrations and the fields needed for each
in order for the user to register
'''
class UserRegistrationForm(forms.Form):
    full_name = forms.CharField(min_length=1, max_length = 50)
    email = forms.EmailField()
    zipcode = forms.CharField(min_length = 5, max_length = 5)
    password = forms.CharField(widget=forms.PasswordInput, max_length = 16, min_length = 6)
    password_confirmation = forms.CharField(widget=forms.PasswordInput, min_length = 6)

    #added the default here for now
    pick_up = forms.CharField(widget=forms.widgets.Textarea(), initial='Pick up at my house.')

    widgets = {
                'password': forms.PasswordInput(),
                'pick_up': forms.Textarea(attrs={'rows': 1, 'cols': 1}),
    }

'''
class for tool registration in order to give the fields needed
to make the tool registration form
'''
class ToolRegistrationForm(forms.Form):
    '''
    Tool Resgistration Form has the forms necessary for adding a tool
    '''
    tool_name = forms.CharField(min_length=1, max_length=20)
    type_of_tool = forms.IntegerField()
    description = forms.CharField(min_length=1, max_length=144)
    condition = forms.IntegerField()
    pick_up_tool = forms.CharField(min_length=1)
    image = forms.FileField(label='Select image', help_text='insert help text', required=False)

class ToolEditForm(forms.Form):
    '''
    Tool Edit Form are the necessary fields for editing tools
    '''
    image = forms.FileField(label='Select image', help_text='insert help text', required=False)
    tool_name = forms.CharField(min_length=1, max_length=100)
    type_of_tool = forms.IntegerField()
    description = forms.CharField(min_length=1, max_length=144)
    condition = forms.IntegerField()
    pick_up_tool = forms.CharField(min_length=1)
    new_shed = forms.IntegerField()
    availability = forms.IntegerField()

class UserEditForm(forms.Form):
    '''
    User Edit form has the necessayr fields in order to edit the current user's profile
    '''
    #profile_image = forms.FileField(label='Select image', help_text='insert help text', required=False)
    full_name = forms.CharField(min_length=1, max_length = 50)
    question1 = forms.IntegerField(required=False)
    answer1 = forms.CharField(max_length=100, required=False)
    question2 = forms.IntegerField(required=False)
    answer2 = forms.CharField(max_length=100, required=False)
    pick_up = forms.CharField(max_length=144)
    address = forms.CharField(max_length=50)
    new_password = forms.CharField(min_length=6, max_length=16, required=False)
    new_password_confirm = forms.CharField(min_length=6, max_length=16, required=False)