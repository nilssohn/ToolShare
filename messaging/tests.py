from django.test import TestCase
from messaging.models import Message
from registration.models import User

from datetime import datetime

class MessagingTests(TestCase):
	def setUp(self):
		"""
		Creates test messages.
		Note: Requires two users already in the system to operate properly.
		"""
		receiving_user = User.objects.get(id=1)
		sending_user = User.objects.get(id=2)
		message1 = Message.objects.create(title="New Personal Message", message="A message", receiving_user=receiving_user, sending_user=sending_user, date_sent=datetime.now())
		return

	def test_message_creation(self):
		"""
		Ensures that messages are being created properly.
		Note: There may not be any messges in the database for this to work.
		"""
		message1 = Message.objects.get(id=1)
		self.assertEqual(message1.message, "A message")
		return