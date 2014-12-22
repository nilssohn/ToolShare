from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
from registration.models import User
from messaging.signals import user_message, shed_message

class Message(models.Model):
	"""
		@author: Grant Gadomski
	"""
	title = models.CharField(max_length=144)
	message = models.TextField(max_length=300)
	receiving_user = models.ForeignKey(User, related_name="receiving_user")
	sending_user = models.ForeignKey(User, related_name="sending_user", default=None, null=True)
	sending_shed = models.CharField(max_length=200, default=None, null=True)
	has_been_viewed = models.BooleanField(default=False)
	date_sent = models.DateTimeField()

@receiver(user_message)
def user_message(sender, **kwargs):
	"""
	@author Grant Gadomski
	"""
	receiving_user = kwargs['receiving_user']
	sending_user = kwargs['sending_user']
	message = kwargs['message']

	the_message = Message(title=("New message from " + sending_user.email),
					message=message,
					receiving_user=receiving_user,
					sending_user=sending_user,
					date_sent=datetime.now()
					)
	the_message.save()
	return

@receiver(shed_message)
def shed_message(sender, **kwargs):
	"""
	@author Grant Gadomski
	"""
	receiving_user = kwargs['receiving_user']
	sending_user = kwargs['sending_user']
	sending_shed = kwargs['sending_shed']
	message = kwargs['message']

	the_message = Message(title=("New message from " + sending_user.email + " in " + sending_shed),
						message=message,
						receiving_user=receiving_user,
						sending_user=sending_user,
						sending_shed=sending_shed,
						date_sent=datetime.now()
						)
	the_message.save()
	return