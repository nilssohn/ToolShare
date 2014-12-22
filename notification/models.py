"""
@authors: Tina Howard, Grant Gadomski, Nick Mattis
Notification class shows the title, message, and checks to see if various things have 
been viewed by the particular user in order to send a Notification for various events
"""

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from registration.models import User, Tool, Reservation
from notification.signals import borrow_request, request_result, tool_borrowed, tool_returned, rating_result, created_new_shed, added_to_shed, message_to_user, message_to_user, tool_deregistered, tool_ready_for_borrow, tool_returned_check, removed_shed, cancel_reservation

from django.dispatch import receiver

class Notification(models.Model):
    '''
    Notifcation class shows everything that that a notification would show 
    '''
    title = models.CharField(max_length = 120)
    notification_type = models.CharField(max_length = 120)
    message = models.TextField()
    start_date = models.DateField(default=None, null=True, blank=True)
    end_date = models.DateField(default=None, null=True, blank=True)
    tool = models.ForeignKey(Tool, related_name="tool", default=None, null=True)
    reservation = models.ForeignKey(Reservation, related_name="reservation", default=None, null=True)
    hasBeenViewed = models.BooleanField(default = False)
    from_user = models.ForeignKey(User, related_name="from_user", default=None, null=True)
    to_user = models.ForeignKey(User, related_name="to_user")

@receiver(borrow_request)
def borrow_request(sender, **kwargs):
    """
        Sends a request to the owner of the tool from the requester of the tool to borrow said tool.
    """
    owner = kwargs['owner']
    requester = kwargs['requester']
    tool_id = kwargs['tool_id']
    start_date = kwargs['start_date']
    end_date = kwargs['end_date']
    message = kwargs['message']
    tool = Tool.objects.get(id=tool_id)

    notification = Notification(title=requester.email + "would like to borrow your " + tool.tool_name + " from " + str(start_date) + " to " + str(end_date),
                                message=message,
                                tool=tool,
                                notification_type="borrow_request",
                                hasBeenViewed=False,
                                to_user=owner,
                                from_user=requester,
                                start_date=start_date,
                                end_date=end_date)

    notification.save()
    return

@receiver(tool_returned_check)
def tool_returned_check(sender, **kwargs):
    """
        Sends a signal requesting the owner of the tool to confirm that the tool has been returned IRL.
    """
    owner = kwargs['owner']
    borrower = kwargs['borrower']
    tool = Tool.objects.get(id=kwargs['tool_id'])
    reservation = Reservation.objects.get(id=kwargs['reservation_id'])

    message = ("Please confirm that this return actually happened")

    notification = Notification(title=(borrower.email + " has returned your " + tool.tool_name),
                                message=message,
                                from_user=borrower,
                                notification_type="tool_returned_check",
                                to_user=owner,
                                tool=tool,
                                reservation=reservation
                                )
    notification.save()
    return

@receiver(request_result)
def request_result(sender, **kwargs):
    """
        Sends a signal to the borrowing requester, either with success if their request was accepted or the reason why if not.
        
        Result will either be something like "Success, you are now borrowing <enter tool here>.", or "User <tool owner> declined your
        borrowing request because <reason>.
    """
    result = kwargs['result']
    owner = kwargs['owner']
    borrower = kwargs['borrower']

    notification = Notification(title="Borrow Request Result",
                                message=result,
                                hasBeenViewed=False,
                                to_user=borrower,
                                from_user=owner
                                )
    notification.save()
    return

@receiver(tool_borrowed)
def tool_borrowed(sender, **kwargs):
    """
        Sends a signal notifying the owner of a tool that their tool has been borrowed.
    """
    owner = kwargs['owner']
    borrower = kwargs['borrower']
    tool = Tool.objects.get(id=kwargs['tool_id'])

    message = (borrower.email + " has borrowed your " + tool.tool_name)

    notification = Notification(title="Tool Borrowed Notification",
                                message=message,
                                hasBeenViewed=False,
                                from_user=borrower,
                                to_user=owner
                                )

    notification.save()
    return

@receiver(tool_returned)
def tool_returned(sender, **kwargs):
    """
        Sends a signal notifying the owner of a tool that their tool has been returned.
    """
    owner = kwargs['owner']
    borrower = kwargs['borrower']
    tool = kwargs['tool']

    message = (borrower.email + " has returned your " + tool.tool_name)

    notification = Notification(title="Tool Returned Notification",
                                message=message,
                                hasBeenViewed=False,
                                notification_type="tool_returned",
                                tool=tool,
                                from_user=borrower,
                                to_user=owner
                                )
                                
    notification.save()

@receiver(tool_ready_for_borrow)
def tool_ready_for_borrow(sender, **kwargs):
    '''
        Allows the tool be be available to pickup once
        reservation is accepted
    '''
    owner = kwargs['owner']
    borrower = kwargs['borrower']
    tool = kwargs['tool']

    message = (tool.tool_name + ", the tool you requested, is now available for pickup.")

    notification = Notification(title="Tool Pickup Available",
                                notification_type="tool_ready_for_borrow",
                                message=message,
                                tool=tool,
                                from_user=owner,
                                to_user=borrower
                                )
    notification.save()
    return

@receiver(rating_result)
def rating_result(sender, **kwargs):
    """
        Sends a signal notifying the former borrower of a tool of the rating given to them by the owner of said tool.
    """
    owner = kwargs['owner']
    borrower = kwargs['borrower']
    comments = kwargs['comments']
    thumb = kwargs['thumb']

    if thumb == "up":
        the_title = (owner.email + " gave you a thumbs up.")
        message = comments
    else:
        the_title = (owner.email + " gave you a thumbs down.")
        message = comments

    notification = Notification(title=the_title,
                                message=message,
                                hasBeenViewed=False,
                                from_user=owner,
                                to_user=borrower
                                )
    notification.save()
    return

@receiver(created_new_shed)
def created_new_shed(sender, **kwargs):
    """
        Sends a notification to the creator of a private shed indicating that their shed has been created successfully.
    """
    shed_name = kwargs['shed_name']
    creator = kwargs['creator']

    notification = Notification(title="New Shed Created",
                                message=("Your new shed " + shed_name + " has been created."),
                                from_user=creator,
                                to_user=creator
                                )
    notification.save()
    return

@receiver(added_to_shed)
def added_to_shed(sender, **kwargs):
    """
        Sends a notification to a user indicating that they've been added to a private shed.
    """
    shed_name = kwargs['shed_name']
    creator = kwargs['creator']
    person_added = kwargs['person_added']

    notification = Notification(title="Added to a Shed",
                                message=(creator.email + " added you to the shed " + shed_name),
                                from_user=creator,
                                to_user=person_added
                                )
    notification.save()
    return

@receiver(tool_deregistered)
def tool_deregistered(sender, **kwargs):
    '''
        sends a notfication to any users that reserved said tool that the tool was tool_deregistered
    '''
    owner = kwargs['owner']
    requester = kwargs['requester']
    tool = kwargs['tool']

    message = (owner.email + " has deregistered the " + tool.tool_name + " you reserved.")
    notification = Notification(title=(owner.email + " has deregistered " + tool.tool_name),
                                message=message,
                                from_user=owner,
                                to_user=requester
                                )
    notification.save()
    return

@receiver(message_to_user)
def message_to_user(sender, **kwargs):
    """
        Sends a personal message to a user from another user.
    """
    message = kwargs['message']
    to_user = kwargs['to_user']
    from_user = kwargs['from_user']

    notification = Notification(title=("Message from " + from_user),
                                message=message,
                                from_user=from_user,
                                to_user=to_user
                                )
    notification.save()
    return

@receiver(removed_shed)
def removed_shed(sender, **kwargs):
    """
    notify a user they have been removed from a shed
    """
    shed_name = kwargs['shed_name']
    user_to_remove = kwargs['user_to_remove']

    notification = Notification(title=("You have been removed from " + shed_name),
                                notification_type="removed_shed",
                                message=shed_name,
                                to_user=user_to_remove,)

    notification.save()
    return

@receiver(cancel_reservation)
def cancel_reservation(sender, **kwargs):
    """
    notify a user that a tool has been moved and their reservation has been cancelled
    """
    shed_name = kwargs['shed_name']
    user_to_cancel = kwargs['user_to_cancel']
    tool = kwargs['tool']
    user_who_cancelled = kwargs['user_who_cancelled']

    notification = Notification(title=("Your reservation has been cancelled"),
                                message=user_who_cancelled.full_name+"'s "+tool.tool_name+"has been removed from "+shed_name,
                                to_user=user_to_cancel,
                                from_user=user_who_cancelled)

    notification.save()
    return