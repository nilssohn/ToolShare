"""
    @author: Grant Gadomski
"""
from django.test import TestCase

from notification.models import Notification
from registration.models import Tool, User

class NotificationTests(TestCase):
    def setUp(self):
        """
            Creates a handful of Notification objects for testing.
            Note: Requires two users and one tool in the system already to operate properly.
        """
        tool1 = Tool.objects.get(id=1)
        from_user1 = User.objects.get(id=1)
        to_user1 = User.objects.get(id=2)

        Notification.objects.create(title="Borrow Request", notification_type="borrow_request", message="grant.gadomski@gmail.com would like to borrow your Can Opener.",
                                    tool=tool1, from_user=from_user1, to_user=to_user1)

        Notification.objects.create(title="Borrow Request Result", notification="borrow_request_result", message="Your request to borrow tina.howard@gmail.com's Can Opener has been declined.",
                                    from_user=from_user1, to_user=to_user1)

        return
        
    def test_notification_creation(self):
        """
            Tests to ensure that Notification objects are being created correctly.
        """
        borrow_request = Notification.objects.get(message="grant.gadomski@gmail.com would like to borrow your Can Opener.")
        borrow_request_result = Notification.objects.get(message="Your request to borrow tina.howard@gmail.com's Can Opener has been declined.")
        from_user1 = User.objects.get(id=1)
        to_user1 = User.objects.get(id=2)
        tool1 = Tool.objects.get(id=1)
        
        self.assertEqual(borrow_request.from_user, from_user1)
        self.assertEqual(borrow_request_result.to_user, to_user1)
        self.assertEqual(borrow_request.tool, tool1)
        self.assertEqual(borrow_request_result.tool, None)
        return