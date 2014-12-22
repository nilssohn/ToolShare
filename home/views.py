"""
    @author Grant Gadomski, Nick Mattis
"""

from django.shortcuts import render
from registration.models import User, Tool, Reservation
from registration.models import SECURITY_QUESTIONS_1, SECURITY_QUESTIONS_2
from sheds.models import Sheds, ShedMember
from home.forms import PasswordRecover, AnswersToQuestions, ShedAddress
from notification.views import Notification
from messaging.models import Message
from notification import signals
from django.http import HttpResponse, HttpResponseRedirect, HttpResponse
from datetime import date
from django.core.urlresolvers import reverse

def index(request):
    """
    Returns the index page.
    """
    return render(request, 'home/index.html')

def answer_questions(request):
    """
    Allows the user to answer their security questions in an effort to change their password.
    """
    alert_type = None
    alert_message = None

    if request.method == 'POST':
        form = PasswordRecover(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']

            user = User.objects.filter(email=username)

            if user:
                if user[0].answer1 == None and user[0].answer2 == None:
                    alert_type = "failure"
                    alert_message = "We've encountered a problem! Your security questions aren't setup."
                    return render(request, 'home/index.html', {'alert_type': alert_type, 'alert_message': alert_message})
                else:
                    return render(request, 'home/answer_questions.html', {'user': User.objects.get(email=username), 'questions1': SECURITY_QUESTIONS_1, 'questions2': SECURITY_QUESTIONS_2, 'question_work': False})
            else:
                alert_type = "failure"
                alert_message = "We didn't find a match for that email!"                
                return render(request, 'home/index.html', {'alert_type': alert_type, 'alert_message': alert_message})
        else:
            alert_type = "failure"
            alert_message = "The email you put in is not proper! (i.e. tool@share.com)"
            return render(request, 'home/index.html', {'alert_type': alert_type, 'alert_message': alert_message})
    else:
        alert_type = "failure"
        alert_message = "The email cannot be blank!"
        return render(request, 'home/index.html', {'alert_type': alert_type, 'alert_message': alert_message})

def give_password(request, user_id):
    """
    Checks if the questions have been answered correctly, if so changes the password and allows the user to change it.
    """
    if request.method == 'POST':
        user = User.objects.filter(id=user_id)[0]
        form = AnswersToQuestions(request.POST)

        if form.is_valid():
            answer1 = form.cleaned_data['answer1']
            answer2 = form.cleaned_data['answer2']

            correct = []
            if user.answer1 != None:
                if user.answer1.lower() == answer1.lower():
                    correct.append(True)
                else:
                    correct.append(False)
            if user.answer2 != None:
                if user.answer2.lower() == answer2.lower():
                    correct.append(True)
                else:
                    correct.append(False)

            if correct.count(False) != 0:
                return render(request, 'home/answer_questions.html', {'user': user, 'questions1': SECURITY_QUESTIONS_1, 'questions2': SECURITY_QUESTIONS_2, 'question_work': True})
            else:
                user.set_password("12345")
                user.save()
                alert_type = "success"
                alert_message = "Your password has been changed to 12345."
                return render(request, 'home/index.html', {'alert_type': alert_type, 'alert_message': alert_message})

        else:
            return HttpResponse(forms.errors)
    else:
        return HttpResponse("Not POST Data.")

def welcome(request):
    '''
    Method checks to see if the user has any tools associated with it or not 
    then checks for any borrowed tools. If they exists they they render
    '''
    user = request.user
    #Checks to see if any of the user's reservations are ready and they are not
    #in possession of the tool yet. If so sends notification to borrow said tool.
    current_date = date.today()
    users_reservations = Reservation.objects.filter(borrower=user)
    for reservation in users_reservations:
        tool = reservation.tool
        if (reservation.start_date >= current_date and reservation.end_date <= current_date):
            if (tool.current_user_of_tool != user):
                if tool.current_user_of_tool != tool.owner_of_tool:
                    #Cancel reservation, send notification.
                    reservation.delete()
                    signals.cancel_reservation.send(sender=None, user_to_cancel=user, tool=tool, user_who_canceled=tool.owner_of_tool, shed_name=tool.current_shed.shed_name)
                else:
                    #Send notification.
                    tool = reservation.tool
                    pickup_available = signals.tool_ready_for_borrow.send(sender=None, owner=tool.owner_of_tool, borrower=user, tool=tool)

    notifications = Notification.objects.filter(to_user=user, hasBeenViewed=False)
    if not notifications:
        notifications = None
    
    user_tools = Tool.objects.filter(owner_of_tool=user)
    if not user_tools:
        user_tools = None

    reservation_list = Reservation.objects.filter(borrower=user).order_by('start_date')
    if (not reservation_list) and (not type(reservation_list) is Reservation):
        reservation_list = None

    user_messages = Message.objects.filter(receiving_user=user).filter(has_been_viewed=False).order_by('-date_sent')
    if len(user_messages) > 0:
        user_message = user_messages[0]
    else:
        user_message = None    
        
    zipcode = user.zipcode
    user_stats = User.objects.filter(zipcode=zipcode)
    times_lended = list(user_stats.order_by('-times_lended'))
    if len(times_lended) == 0:
        time_lended == None
    else:
        time_lended = times_lended[0]
    
    times_borrowed = list(user_stats.order_by('-times_borrowed'))
    if len(times_borrowed) == 0:
        time_borrowed = None
    else:
        time_borrowed = times_borrowed[0]
        
    tool_stats = Tool.objects.filter(tool_zipcode=zipcode)
    times_used = list(tool_stats.order_by('-uses'))
    if len(times_used) == 0:
        time_used = None
    else:
        time_used = times_used[0]
        
    dates_used = list(tool_stats.order_by('date_last_used'))
    if len(dates_used) == 0:
        date_used = None
    else:
        date_used = dates_used[0]
        
    ratings_stats = User.objects.filter(zipcode=zipcode)
    thumbs_up = list(ratings_stats.order_by('-thumbs_up'))
    if len(thumbs_up) == 0:
        thumb_up = None
    else:
        thumb_up = thumbs_up[0]

    community_shed = Sheds.objects.get(shed_zipcode=user.zipcode, shed_type=1)
    if community_shed.shed_address == None:
        c_address = True    #user does need to add address
    else:
        c_address = False   #shed already has an address


    return render(request, 'home/welcome.html', {'user': user, 'community_address': c_address, 'notifications': notifications, 'tools': user_tools, 'reservation_list': reservation_list, 'user_message': user_message, 'today':date.today(),
                                                'time_lended': time_lended, 'time_borrowed': time_borrowed, 'time_used': time_used, 'date_used': date_used, 'thumb_up': thumb_up})

def add_community_shed_address(request, zipcode):
    """
    asks user to give address for community shed if they are the
    first one to register for that share zone
    """
    if request.method == 'POST':
        form = ShedAddress(request.POST)

        if form.is_valid():
            address = form.cleaned_data['address']

            community_shed = Sheds.objects.get(shed_zipcode=zipcode, shed_type=1)
            community_shed.shed_address = address

            alert_type = "success"
            alert_message = "Address added!"
 
            community_shed.save()

            user = request.user
            current_date = date.today()
            users_reservations = Reservation.objects.filter(borrower=user)
            for reservation in users_reservations:
                tool = reservation.tool
                if (reservation.start_date >= current_date and reservation.end_date <= current_date):
                    if (tool.current_user_of_tool != user):
                        #Send notification.
                        tool = reservation.tool
                        pickup_available = signals.tool_ready_for_borrow.send(sender=None, owner=tool.owner_of_tool, borrower=user, tool=tool)

            notifications = Notification.objects.filter(to_user=user, hasBeenViewed=False)
            if not notifications:
                notifications = None
            
            user_tools = Tool.objects.filter(owner_of_tool=user)
            if not user_tools:
                user_tools = None

            reservation_list = Reservation.objects.filter(borrower=user).order_by('start_date')
            if (not reservation_list) and (not type(reservation_list) is Reservation):
                reservation_list = None

            user_messages = Message.objects.filter(receiving_user=user).order_by('-date_sent')
            if len(user_messages) > 0:
                user_message = user_messages[0]
            else:
                user_message = None    
                
            zipcode = user.zipcode
            user_stats = User.objects.filter(zipcode=zipcode)
            times_lended = list(user_stats.order_by('-times_lended'))
            if len(times_lended) == 0:
                time_lended == None
            else:
                time_lended = times_lended[0]
            
            times_borrowed = list(user_stats.order_by('-times_borrowed'))
            if len(times_borrowed) == 0:
                time_borrowed = None
            else:
                time_borrowed = times_borrowed[0]
                
            tool_stats = Tool.objects.filter(tool_zipcode=zipcode)
            times_used = list(tool_stats.order_by('-uses'))
            if len(times_used) == 0:
                time_used = None
            else:
                time_used = times_used[0]
                
            dates_used = list(tool_stats.order_by('date_last_used'))
            if len(dates_used) == 0:
                date_used = None
            else:
                date_used = dates_used[0]
                
            ratings_stats = User.objects.filter(zipcode=zipcode)
            thumbs_up = list(ratings_stats.order_by('-thumbs_up'))
            if len(thumbs_up) == 0:
                thumb_up = None
            else:
                thumb_up = thumbs_up[0]

            community_shed = Sheds.objects.get(shed_zipcode=user.zipcode, shed_type=1)
            if community_shed.shed_address == None:
                c_address = True    #user does need to add address
            else:
                c_address = False   #shed already has an address


            return render(request, 'home/welcome.html', {'user': user, 'community_address': c_address, 'notifications': notifications, 'tools': user_tools, 'reservation_list': reservation_list, 'user_message': user_message, 'today':date.today(),
                                                        'time_lended': time_lended, 'time_borrowed': time_borrowed, 'time_used': time_used, 'date_used': date_used, 'thumb_up': thumb_up, 'alert_type': alert_type, 'alert_message': alert_message})        
        else:
            return HttpResponse(forms.errors)
    else:
        return HttpResponse("Not POST Data.")

def get_started(request):
    return render(request, 'home/get_started.html')

def remove_tools(request, notification_id):
    """
    get list of tools that user needs to move from shed
    """
    user = request.user
    notification = Notification.objects.get(id=notification_id)
    shed = Sheds.objects.get(shed_name=notification.message)
    user_sheds = Sheds.objects.filter(user=user)
    tools = Tool.objects.filter(owner_of_tool=user, current_shed=shed)
    #print(tools)
    if tools:
        return render(request, 'home/remove_tools.html', {'tools': tools, 'sheds': user_sheds, 'notification': notification})
    else:
        notification.delete()
        return HttpResponseRedirect(reverse('home:welcome', args=()))

def move_tool(request, notification_id, tool_id):
    """
    move tool and check to see if any of their tools are left in the shed
    then delete notification once all tools were moved
    """
    user = request.user
    tool_to_move = Tool.objects.get(id=tool_id)
    notification = Notification.objects.get(id=notification_id)
    shed = Sheds.objects.get(shed_name=notification.message)
    user_sheds = Sheds.objects.filter(user=user)
    tools = Tool.objects.filter(owner_of_tool=user, current_shed=shed)

    location = request.POST['new_shed']

    new_shed = Sheds.objects.get(id=location)
    #print(new_shed.shed_name)
    tool_to_move.current_shed = new_shed
    tool_to_move.save()

    if tools:
        return render(request, 'home/remove_tools.html', {'tools' : tools, 'sheds': user_sheds, 'notification': notification})
    else:
        notification.delete()
        return HttpResponseRedirect(reverse('home:welcome', args=()))
