"""
@author Nick Mattis
"""

from django.test import TestCase
from django.test.utils import setup_test_environment
from registration.models import User, Tool, ShareZone
from sheds.models import Sheds, ShedMember

setup_test_environment()

class  M2MThroughTest(TestCase):
    """
    testing Many to Many relationship through a centralized database. This is used to link
    users to their sheds and sheds to their respective users using a ShedMember table that holds
    what type of memeber they are and the foreign keys for user and shed that you are referencing.
    """
    def setUp(self):
        #create a share zone
        self.zone = ShareZone.objects.create(zone='14623')

        # Create 4 users
        self.bob = User.objects.create(full_name='Bob', email='bob@gmail.com', zipcode='14623', pick_up='this is a test', password='password', my_zone=self.zone)
        self.nick = User.objects.create(full_name='Nick', email='nick@gmail.com', zipcode='14623', pick_up='this is a test', password='password', my_zone=self.zone)
        self.nils = User.objects.create(full_name='Nils', email='nils@gmail.com', zipcode='14623', pick_up='this is a test', password='password', my_zone=self.zone)
        self.tina = User.objects.create(full_name='Tina', email='tina@gmail.com', zipcode='14623', pick_up='this is a test', password='password', my_zone=self.zone)

        #create a community shed
        self.community = Sheds.objects.create(shed_name='community', shed_type=1)

        #create private sheds
        self.private1 = Sheds.objects.create(shed_name='private1', shed_type=2)
        self.private2 = Sheds.objects.create(shed_name='private2', shed_type=2)
        self.private3 = Sheds.objects.create(shed_name='private3', shed_type=2)
        self.private4 = Sheds.objects.create(shed_name='private4', shed_type=2)

        #create home sheds
        self.bobhome = Sheds.objects.create(shed_name='bob', shed_type=3)
        self.nickhome = Sheds.objects.create(shed_name='nick', shed_type=3)
        self.nilshome = Sheds.objects.create(shed_name='nils', shed_type=3)
        self.tinahome = Sheds.objects.create(shed_name='tina', shed_type=3)

        #create link to community shed
        ShedMember.objects.create(user=self.bob, shed=self.community, member_type=5)
        ShedMember.objects.create(user=self.nick, shed=self.community, member_type=5)
        ShedMember.objects.create(user=self.nils, shed=self.community, member_type=5)
        ShedMember.objects.create(user=self.tina, shed=self.community, member_type=5)

        #every person is a member of every group but bob is the coordinator for the
        #first private shed and nick and nils are the coordinators for the second one
        ShedMember.objects.create(user=self.bob, shed=self.private1, member_type=4)
        ShedMember.objects.create(user=self.nick, shed=self.private1, member_type=5)
        ShedMember.objects.create(user=self.nils, shed=self.private1, member_type=5)
        ShedMember.objects.create(user=self.tina, shed=self.private1, member_type=5)
        
        ShedMember.objects.create(user=self.bob, shed=self.private2, member_type=5)
        ShedMember.objects.create(user=self.nick, shed=self.private2, member_type=4)
        ShedMember.objects.create(user=self.nils, shed=self.private2, member_type=4)
        ShedMember.objects.create(user=self.tina, shed=self.private2, member_type=5)

        ShedMember.objects.create(user=self.bob, shed=self.private3, member_type=5)
        ShedMember.objects.create(user=self.nick, shed=self.private3, member_type=5)
        ShedMember.objects.create(user=self.nils, shed=self.private3, member_type=4)
        ShedMember.objects.create(user=self.tina, shed=self.private3, member_type=5)

        ShedMember.objects.create(user=self.bob, shed=self.private4, member_type=5)
        ShedMember.objects.create(user=self.nick, shed=self.private4, member_type=4)
        ShedMember.objects.create(user=self.nils, shed=self.private4, member_type=4)
        ShedMember.objects.create(user=self.tina, shed=self.private4, member_type=4)

        #create link to home shed
        ShedMember.objects.create(user=self.bob, shed=self.bobhome, member_type=4)
        ShedMember.objects.create(user=self.nick, shed=self.nickhome, member_type=4)
        ShedMember.objects.create(user=self.nils, shed=self.nilshome, member_type=4)
        ShedMember.objects.create(user=self.tina, shed=self.tinahome, member_type=4)

    def test_unfiltered_membership(self):
        """
        is nils the only one who know about his home shed?
        """
        nils_sheds = Sheds.objects.filter(user=self.nils, shed_type=3)
        self.assertEqual(nils_sheds[0], self.nilshome)

    def test_coordinator_membership(self):
        """
        does nils know about the sheds that he is coordinator for?
        """
        nils_sheds = Sheds.objects.filter(user=self.nils, membership__member_type=4)
        sheds =[]
        for shed in nils_sheds:
            sheds.append(shed.shed_name)
        self.assertEqual(sheds, [self.private2.shed_name, self.private3.shed_name, self.private4.shed_name, self.nilshome.shed_name])

    def test_member_membership(self):
        """
        does nils know about the sheds that he is only a member of?
        """
        nils_sheds = Sheds.objects.filter(user=self.nils, membership__member_type=5)
        sheds =[]
        for shed in nils_sheds:
            sheds.append(shed.shed_name)
        self.assertEqual(sheds, [self.community.shed_name, self.private1.shed_name])

    def test_shed_membership(self):
        """
        does a shed know about all its members?
        """
        users = User.objects.filter(shed=self.private1)
        ulist = []
        for user in users:
            ulist.append(user.full_name)

        self.assertEqual(ulist, ['Bob', 'Nick', 'Nils', 'Tina'])

    def test_getting_by_shed_name(self):
        """
        Ensures that you can fetch sheds by shed name.
        """
        shed = Sheds.objects.filter(shed_name='community')[0].id
        shed_object = Sheds.objects.get(pk=shed)
        self.assertEqual(shed_object, self.community)