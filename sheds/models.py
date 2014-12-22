"""
    @author Grant Gadomski, Nick Mattis
"""
from django.db import models

COMMUNITY = 1
PRIVATE = 2
HOME = 3
COORADINATOR = 4
MEMBER = 5

USER_TYPES = (
    (COORADINATOR, 'cooradinator'),
    (MEMBER, 'member'),
)

SHED_TYPES = (
    (COMMUNITY, 'Community'),
    (PRIVATE, 'Private'),
    (HOME, 'Home'),
)

def validate_zip(value):
    """
    Ensures that the zipcode is truely one.
    """
    if not value.isdigit():
        raise ValidationError('Zipcode must be a number')
    elif len(value) != 5:
        raise ValidationError('Zipcode must be a lenght of 5')

class Sheds(models.Model):
    """
    Gives the Private and community shed an integer to check for later
    """
    shed_name = models.CharField(max_length=20, unique=True)
    shed_type = models.IntegerField(choices=SHED_TYPES, default=HOME)
    shed_zipcode = models.CharField(validators = [validate_zip], max_length=5)
    shed_address = models.CharField(max_length=50, null=True)

    users = models.ManyToManyField('registration.User', through='sheds.ShedMember', related_name='shed')

class ShedMember(models.Model):
    """
    Defines the relationship between a user and a private shed and what type of
    user for that shed they are wether it be a cooradinator or just member
    """
    user = models.ForeignKey('registration.User', related_name='membership')
    shed = models.ForeignKey(Sheds, related_name='membership')
    member_type = models.IntegerField(choices=USER_TYPES)