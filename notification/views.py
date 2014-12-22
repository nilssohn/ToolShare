"""
@authors Tina Howard, Grant Gadomski
"""

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from notification.models import Notification
from notification import signals
from datetime import date

def show_notifications(request):
    """
        Fetches all notifications sent to the user who's id = user_id, renders notification.html with set of
        notifications passed in.
    """
    user = request.user
    notifications = Notification.objects.filter(to_user=user)

    return render(request, 'home/welcome.html', {'notifications': notifications})

'''
delete_notification shows the notification if its related to that particular user
'''
def delete_notification(request, notification_id):
    n = Notification.objects.get(id = notification_id)
    n.hasBeenViewed = True

def mark_as_read(request, notification_id):
    """
        Marks the notification as read so that it isn't presented in the user's notification page anymore.
    """
    notification = Notification.objects.get(id=notification_id)
    notification.hasBeenViewed = True
    notification.save()

    return HttpResponseRedirect(reverse('home:welcome', args=()))

def mark_all_as_read(request):
    """
    Marks all notifications directed towards the user as read.
    """
    notifications = Notification.objects.filter(to_user=request.user)
    for notification in notifications:
        if not notification.notification_type:
            notification.hasBeenViewed = True
            notification.save()

    return HttpResponseRedirect(reverse('home:welcome', args=()))

def rate_user(request, notification):
    """
        Allows the owner of a tool to rate the borrower upon return of said tool.
    """
    tool = notification.tool
    borrower = notification.from_user

    return render(request, 'notification/rate_user.html', {'notification': notification, 'tool': tool, 'borrower': borrower})

def send_rating(request, notification_id):
    """
        Sends a new notification to the former borrower of the tool informing them of the owner's rating of them.
    """
    notification_id = str(int(notification_id)-1)
    notification = Notification.objects.filter(id=(notification_id))[0]
    tool = notification.tool
    owner = notification.to_user
    borrower = notification.from_user
    
    if (request.POST['thumb'] == "Give a Thumbs Up!"):
        thumb = "up"
    else:
        thumb = "down"

    if thumb == "up":
        borrower.thumbs_up += 1
    else:
        borrower.thumbs_down += 1
    borrower.save()

    notification.hasBeenViewed = True
    notification.save()
    
    comments = request.POST['comments']
    rating_result = signals.rating_result.send(sender=None, owner=owner, borrower=borrower, comments=comments, thumb=thumb)
    
    return HttpResponseRedirect(reverse('notification:show_notifications', args=()))