from django.shortcuts import render
from messaging import signals
from registration.models import User
from registration.views import user_profile
from messaging.models import Message
from sheds.models import Sheds
from sheds.views import view_shed
from datetime import date

def message_user(request, user_id):
	"""
	Sends the message to the user.
	"""
	receiving_user = User.objects.get(id=user_id)
	message = request.POST['message']

	user_message = signals.user_message.send(sender=None, receiving_user=receiving_user, sending_user=request.user, message=message)
	return user_profile(request, receiving_user.id)

def message_shed(request, shed_id):
	"""
	Sends message to all users in shed.
	"""
	to_shed = Sheds.objects.get(id=shed_id)
	message = request.POST['message']
	#Loop through people in shed, sending a note to each one.
	users = User.objects.filter(shed=to_shed)
	for user in users:
		if (user != request.user):
			shed_message = signals.shed_message.send(sender=None, receiving_user=user, sending_user=request.user, sending_shed=to_shed.shed_name, message=message)

	return view_shed(request, to_shed.id, False, False)


def view_messages(request):
	"""
	Renders a page showing the 20 latest messages sent to the current user.
	"""
	messages = Message.objects.filter(receiving_user=request.user).filter(has_been_viewed=False).order_by('-date_sent')[:20]
	return render(request, 'messaging/view_messages.html', {'messages': messages})

def mark_message_as_viewed(request, message_id):
	"""
	Marks a message as viewed, ensuring that the user doesn't see it anymore.
	"""
	message = Message.objects.get(id=message_id)
	message.has_been_viewed = True
	message.save()

	return view_messages(request)