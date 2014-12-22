"""
@authors Nick Mattis, Grant Gadomski, Nils Sohn
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from sheds.models import Sheds

#security question int values
Q1 = 13
Q2 = 14
Q3 = 15
Q4 = 16
Q5 = 17
Q6 = 18

#security question text values
SECURITY_QUESTIONS_1 = (
    (Q1, 'What was the house number and street name you lived in as a child?'),
    (Q2, 'What primary school did you attend?'),
    (Q3, 'In what town or city was your first full time job?'),
)

SECURITY_QUESTIONS_2 = (
    (Q4, 'What is the middle name of your oldest child?'),
    (Q5, 'What are the last five digits of your driver\'s licence number?'),
    (Q6, 'In which city were you born?'),
)

#tool category int values
LAWN_GARDEN = 6
HAND_TOOLS = 7
POWER_TOOLS = 8
CLEANING_TOOLS = 9
AUTOMOTIVE = 10
SAFTEY = 11
OTHER = 12

#text values for tool categories
TYPES_OF_TOOLS = (
    (LAWN_GARDEN, 'Lawn & Garden Tools'),
    (HAND_TOOLS, 'Hand Tools'),
    (POWER_TOOLS, 'Power Tools'),
    (CLEANING_TOOLS, 'Cleaning Tools'),
    (AUTOMOTIVE, 'Automotive Tools'),
    (SAFTEY, 'Safety'),
    (OTHER, 'Other'),
)

#condition ints for a tool
NEW = 0
LIKE_NEW = 1
GOOD = 2
FAIR = 3

#holds the text values for condition of a tool
CONDITIONS = (
    (NEW, 'New'),
    (LIKE_NEW, 'Like New'),
    (GOOD, 'Good'),
    (FAIR, 'Fair'),
)

#is the tool available to borrow or not
AVAILABLE = 4
NOT_AVAILABLE = 5

#text values for the tools availablity
AVAILABILITY = (
    (AVAILABLE, 'Available'),
    (NOT_AVAILABLE, 'Not Available'),
)

class ShareZone(models.Model):
    """
    stores each zip code that has registered at least
    one toolshare User
    """
    zone = models.CharField(max_length=5)

class CustomUserManager(BaseUserManager):
    def create_user(self, full_name, email, password, zipcode, share_zone, pick_up):
        """
            Manager used for creating a new normal user. Necicarry for admin functionality.
        """
        user = self.model(full_name=full_name, email=email, zipcode=zipcode, my_zone=share_zone,
                          pick_up=pick_up, is_staff=False, is_active=True,
                          is_superuser=False)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
            Manager used for creating a new super user or "admin".
        """
        full_name = "Admin"
        zipcode="00000"
        my_zone = ShareZone(00000)
        pick_up = "None"

        user = self.create_user(full_name, email, password, zipcode, my_zone, pick_up)
        user.is_staff = True
        user.is_superuser=True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    """
    Values instered by user at registration.
    @param AbstractBaseUser: The base for user, required to create custom user class.
    """
    #profile_image = models.FileField(upload_to='profileimg/%Y/%m/%d', null=True)
    full_name = models.CharField(max_length=50)
    email = models.CharField(max_length=50, unique=True, db_index=True)
    zipcode = models.CharField(max_length=5)
    pick_up = models.CharField(max_length=144) #S/O to Jen
    my_zone = models.ForeignKey(ShareZone, related_name='my_zone')  #maps user to specific sharezone
    question1 = models.IntegerField(null=True)
    answer1 = models.CharField(max_length=100, null=True)
    question2 = models.IntegerField(null=True)
    answer2 = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=50, null=True)

    sheds = models.ManyToManyField('sheds.Sheds', through='sheds.ShedMember', related_name='user')
    times_lended = models.IntegerField(default=0)
    times_borrowed = models.IntegerField(default=0)
    thumbs_up = models.IntegerField(default=0)
    thumbs_down = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    objects = CustomUserManager()

    def __unicode__(self):
        return self.email
        
    def get_short_name(self):
        return self.email
        
    def get_full_name(self):
        return self.email

class Tool(models.Model):
    """
    values and fields for a tool registration
    """

    tool_name = models.CharField(max_length=20)
    owner_of_tool = models.ForeignKey(User, related_name='owner_of_tool')
    current_user_of_tool = models.ForeignKey(User, related_name='current_user_of_tool', null=True, blank=True)
    type_of_tool = models.IntegerField(choices=TYPES_OF_TOOLS, default=OTHER)
    description = models.CharField(max_length=144)
    condition = models.IntegerField(choices=CONDITIONS)
    availability = models.IntegerField(choices=AVAILABILITY, default=NOT_AVAILABLE)
    tool_zipcode = models.CharField(max_length=5)
    current_shed = models.ForeignKey(Sheds, related_name='current_shed')
    pick_up_tool = models.CharField(max_length=144)
    
    image = models.FileField(upload_to='toolimg/%Y/%m/%d')  #stores image in location based on when it was uploaded
                                                              #the actual getting of the file has to be done by the form.py
                                                              #Need to run "python manage.py sql registration" then syncdb upon
                                                              #reinstation of this feature.'
                                                              #, default='settings.MEDIA_ROOT/toolimg/defaults/other.jpg'
    uses = models.IntegerField(default=0)
    date_last_used = models.DateTimeField(null=True)

class Reservation(models.Model):
    """
    start and end dates for reserving a tool
    """
    start_date = models.DateField('Start of Date', null=True)
    end_date = models.DateField('End of Date', null=True)
    tool = models.ForeignKey(Tool, related_name='related_tool')
    borrower = models.ForeignKey(User, related_name='borrower')