"""
    @author Grant Gadomski
"""
from django.test import TestCase

from statistics.models import UserStatistics, ToolStatistics
from registration.models import User, Tool

class UserStatisticsTests(TestCase):
    def setUp(self):
        """
            Sets up the testing database for testing UserStatistics.
            Note: Must have at least 2 users in the database for this to run correctly.
        """
        user1 = User.objects.get(id=1)
        user2 = User.objects.get(id=2)
        
        UserStatistics.objects.create(user=user1, times_lended=1, times_borrowed=2)
        UserStatistics.objects.create(user=user2)
        
    def test_user_statistics_creation(self):
        """
            Tests for proper creation of UserStatistics objects.
        """
        user1 = User.objects.get(id=1)
        user2 = User.objects.get(id=2)
    
        stat1 = UserStatistics.objects.get(user=user1)
        stat2 = UserStatistics.objects.get(user=user2)
        
        self.assertEqual(stat1.times_lended, 1)
        self.assertEqual(stat2.times_borrowed, 0)
        
class ToolStatisticsTests(TestCase):
    def setUp(self):
        """
            Sets up the testing database for testing ToolStatistics.
            Note: Must have at least 2 tools in the database.
        """
        tool1 = Tool.objects.get(id=1)
        tool2 = Tool.objects.get(id=2)
        
        ToolStatistics.objects.create(the_tool=tool1, uses=5)
        ToolStatistics.objects.create(the_tool=tool2)
        
    def test_tool_statistics_creation(self):
        """
            Ensures proper creation of ToolStatistics objects.
        """
        tool1 = Tool.objects.get(id=1)
        tool2 = Tool.objects.get(id=2)
    
        stat1 = ToolStatistics.objects.get(the_tool=tool1)
        stat2 = ToolStatistics.objects.get(the_tool=tool2)
        
        self.assertEqual(stat1.uses, 5)
        self.assertEqual(stat2.uses, 0)