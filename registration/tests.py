"""
@author Nils Sohn
"""

from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.core.urlresolvers import reverse
from registration.models import User, Tool, ShareZone, Reservation
from sheds.models import Sheds
from registration.models import User

setup_test_environment()

class RegistrationTest(TestCase):
	"""
	Tests user class in the registration module to make sure that all error checking is handled properly

	"""
	def setUp(self):
		# Set up 
		self.zone = ShareZone.objects.create(zone='14623')
		self.bob = User.objects.create(full_name='Bob', email='bob@gmail.com', zipcode='14623', pick_up='this is a test', password='password', my_zone=self.zone)
		self.nick = User.objects.create(full_name='Nick', email='nick@gmail.com', zipcode='14623', pick_up='this is a test', password='password', my_zone=self.zone)
		self.nils = User.objects.create(full_name='Nils', email='nils@gmail.com', zipcode='14623', pick_up='this is a test', password='password', my_zone=self.zone)
		self.tina = User.objects.create(full_name='Tina', email='tina@gmail.com', zipcode='14623', pick_up='this is a test', password='password', my_zone=self.zone)

		self.community = Sheds.objects.create(shed_name='community', shed_type=1)

		self.tool1 = Tool.objects.create(tool_name='1', owner_of_tool=self.bob, current_user_of_tool=None, type_of_tool=1, description='tool', condition=1, availability=1, tool_zipcode='14623', current_shed=self.community, pick_up_tool='home')
		self.tool2 = Tool.objects.create(tool_name='2', owner_of_tool=self.bob, current_user_of_tool=None, type_of_tool=1, description='tool', condition=1, availability=1, tool_zipcode='14623', current_shed=self.community, pick_up_tool='home')
		self.tool3 = Tool.objects.create(tool_name='3', owner_of_tool=self.nick, current_user_of_tool=None, type_of_tool=1, description='tool', condition=1, availability=1, tool_zipcode='14623', current_shed=self.community, pick_up_tool='home')
		self.tool4 = Tool.objects.create(tool_name='4', owner_of_tool=self.nils, current_user_of_tool=None, type_of_tool=1, description='tool', condition=1, availability=1, tool_zipcode='14623', current_shed=self.community, pick_up_tool='home')
		self.tool5 = Tool.objects.create(tool_name='5', owner_of_tool=self.tina, current_user_of_tool=self.nils, type_of_tool=1, description='tool', condition=1, availability=1, tool_zipcode='14623', current_shed=self.community, pick_up_tool='home')
		self.tool6 = Tool.objects.create(tool_name='6', owner_of_tool=self.tina, current_user_of_tool=self.bob, type_of_tool=1, description='tool', condition=1, availability=1, tool_zipcode='14623', current_shed=self.community, pick_up_tool='home')

		Reservation.objects.create(start_date=None, end_date=None, tool=self.tool1, borrower=self.bob)
		Reservation.objects.create(start_date=None, end_date=None, tool=self.tool3, borrower=self.tina)
		Reservation.objects.create(start_date=None, end_date=None, tool=self.tool4, borrower=self.tina)
		Reservation.objects.create(start_date=None, end_date=None, tool=self.tool5, borrower=self.nils)



	def test_user_sharezone(self):
		# Check user creation
		users = User.objects.filter(zipcode='14623')
		self.assertEqual(len(users), 4)

	def test_owner_tool(self):
		# Check owner of tool
		tinas_tools = Tool.objects.filter(owner_of_tool=self.tina)
		self.assertEqual(len(tinas_tools), 2)
		bobs_tools = Tool.objects.filter(owner_of_tool=self.bob)
		self.assertEqual(len(bobs_tools), 2)

	def test_borrower(self):
		# Check borrower of tool
		borrowed_tool = Tool.objects.get(tool_name='6')
		self.assertEqual(borrowed_tool.current_user_of_tool, self.bob)
		borrowed_tool = Tool.objects.get(tool_name='5')
		self.assertEqual(borrowed_tool.current_user_of_tool, self.nils)

	def test_tool_shed(self):
		tools_in_com_shed = Tool.objects.filter(current_shed=self.community)
		self.assertEqual(len(tools_in_com_shed), 6)

	def test_reservations(self):
		reservation = Reservation.objects.get(borrower=self.bob)
		self.assertEqual(reservation.tool, self.tool1)
