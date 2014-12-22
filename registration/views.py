"""
    @authors Tina Howard, Grant Gadomski, Nick Mattis, Laura Silva, Nils Sohn
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.utils.datastructures import MultiValueDictKeyError
from django.http import Http404, HttpResponseRedirect, HttpResponse #TODO Take off HttpResponse after figuring out form error problem.
from django.core.urlresolvers import reverse

from django.core.exceptions import ValidationError
from django.db import IntegrityError

from django.contrib.auth import authenticate, login
from django.contrib.auth import login as django_login, authenticate, logout as django_logout

from datetime import datetime, timedelta, date

from registration.models import ShareZone
from registration.models import TYPES_OF_TOOLS, CONDITIONS, AVAILABILITY
from registration.models import SECURITY_QUESTIONS_1, SECURITY_QUESTIONS_2
from registration.models import User, Tool, Reservation
from registration.forms import UserRegistrationForm, ToolRegistrationForm, ToolEditForm, UserEditForm,LoginForm
from notification import signals
from notification.models import Notification
from notification.views import rate_user
from sheds.models import Sheds, ShedMember
from messaging.models import Message
import sys

def user_login(request):
    """
        Takes in login attempt, logs the user in if correct or redirects back to index if not.
    """
    email = request.POST['email']
    password = request.POST['password']

    try:
        email_check = User.objects.get(email=email)
    except User.DoesNotExist:
        return render(request, 'home/index.html', {'password': True, 'user': False})
        
    user = authenticate(email=email, password=password)
    if (user is not None):
        django_login(request, user)
        return HttpResponseRedirect(reverse('home:welcome', args=()))
    else:
        return render(request, 'home/index.html', {'password': False, 'user': True})
  
def user_profile(request, user_id):
    '''
    Shows the user's profile and the tools that owner owns
    '''
    user = User.objects.get(id=user_id)   
    tools = Tool.objects.filter(owner_of_tool=user)
    if user == request.user:
        is_user = True
    else:
        is_user = False

    return render(request, 'registration/user_profile.html',{'tools':tools, 'the_user':user, 'is_user': is_user, 'tool_types': TYPES_OF_TOOLS, 'conditions': CONDITIONS})

def show_user_messages(request, user_id):
    '''
    Part of the messaging app, that shows the message that were sent to that user
    '''
    user = User.objects.get(id=user_id)
    #Get all messages either with the to_user being the request.user and from_user being the var user, or the to_user
    #being the var user and the from_user being the request.user.
    to_messages = list(Message.objects.filter(receiving_user=user, sending_user=request.user))
    from_messages = list(Message.objects.filter(receiving_user=request.user, sending_user=user))
    all_messages_unsorted = (to_messages + from_messages)
    all_messages = sorted(all_messages_unsorted, key=lambda x: x.date_sent, reverse=True)

    if len(all_messages) == 0:
        messages = None
    else:
        if len(all_messages) < 10:
            messages = all_messages
        else:
            messages = all_messages[:10]
        messages.reverse()

    return render(request, 'registration/show_user_messages.html', {'messages': messages, 'profile_user': user})

def user_logout(request):
    """
        Logs the currently logged-in user out.
    """
    django_logout(request)
    request.session.flush()
    return HttpResponseRedirect(reverse('home:index', args=()))

def user_registration(request):
    """
        Renders the form for the new user to create an account.
        @param request: A HTTP request object.
        @returns: A render of user_registration.html.
    """
    form = UserRegistrationForm()
    return render(request, 'registration/user_registration.html', {'form': form, 'email_not_unique': False, 'password': False}) #Renders registration page.   

def register_user(request):
    """
        Takes in the user registration data from the template, checks to make sure it's all valid, saves to model.
        @param request: A HTTP request object.
        @returns: A redirect to the new user's dashboard if successful, a re-render of the form if not.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            full_name = form.cleaned_data['full_name']
            email = form.cleaned_data['email']
            zipcode = form.cleaned_data['zipcode']
            password = form.cleaned_data['password']
            password_confirmation = form.cleaned_data['password_confirmation']
            pick_up = form.cleaned_data['pick_up']

            if full_name.isspace():
                return render(request, 'registration/user_registration.html', {'form': form, 'email_not_unique': False, 'password': False, 'whitespace':True})

            if (password == password_confirmation):
                share_zone = ShareZone(request.POST['zipcode'])
                share_zone.save()

                user = User(full_name=full_name, email=email, password=password,
                            zipcode=zipcode, my_zone=share_zone, pick_up=pick_up)
                user.set_password(request.POST['password'])
            else:
                return render(request, 'registration/user_registration.html', {'form': form, 'email_not_unique': False, 'password': True, 'whitespace':False})
            
            try:
                user.save()
            except IntegrityError:
                return (render(request, 'registration/user_registration.html', {'form': form, 'email_not_unique': True, 'password': False,"whitespace": False}))

            """
            creates a community shed if one does not exists and sets up the relationship between the new user and shed
            if the community shed for that zipcode already exists then just add relationship for the new user
            """ 
            if not Sheds.objects.filter(shed_zipcode=zipcode, shed_type=1):
                community_shed = Sheds.objects.create(shed_name='Community'+ str(zipcode), shed_type=1, shed_zipcode=zipcode)
                community_shed.save()
                member = ShedMember.objects.create(user=user, shed=community_shed, member_type=4)
                member.save()
            else:
                community_shed = Sheds.objects.filter(shed_zipcode=zipcode, shed_type=1)[0]
                member = ShedMember.objects.create(user=user, shed=community_shed, member_type=5)
                member.save()

            #create a home shed and relationship for the new user
            home_shed = Sheds.objects.create(shed_zipcode=zipcode, shed_type=3, shed_name=user.email, shed_address=user.address)
            home_shed.save()
            membership = ShedMember.objects.create(user=user, shed=home_shed, member_type=4)
            membership.save()

            new_user = authenticate(email=email, password=password)
            login(request, new_user)

            return HttpResponseRedirect(reverse('home:get_started', args=()))
        else:
            #return HttpResponse(user_registration_form.errors) #Use this one to see where the form is failing validation.
            return(render(request, 'registration/user_registration.html', {'form': form, 'email_not_unique': False}))
    else:
        return render(request, 'home/index')

def tool_registration(request):
    """
        Renders the form for the user to add a tool to their account.
        @param request: A HTTP request object.
        @returns: A rendering of tool_registration.html.
    """
    form = ToolRegistrationForm()
    return render(request, 'registration/tool_registration.html', {'form': form, 'tool_types' : TYPES_OF_TOOLS, 'conditions' : CONDITIONS, 'current_user': request.user}) #Render tool registration class.

def register_tool(request):
    """
        Takes in the tool registration data from the template, checks to make sure it's all valid, saves to model.
        @param request: A HTTP request object.
        @returns: A redirect to the user's dashboard if successful, a re-render fo the form if not.
    """
    if request.method == 'POST':
        form = ToolRegistrationForm(request.POST, request.FILES)
        current_user = request.user
        tool_owner = current_user
        tool_zipcode = current_user.zipcode
        home_shed = Sheds.objects.filter(user=current_user, shed_type=3)[0]

        if form.is_valid():
            tool_name = form.cleaned_data['tool_name']
            type_of_tool = form.cleaned_data['type_of_tool']
            description = form.cleaned_data['description']
            condition = form.cleaned_data['condition']
            pick_up_tool = form.cleaned_data['pick_up_tool']
            image = form.cleaned_data['image']
            print(image)

            if image == None:
                image = "toolimg/defaults/" + str(type_of_tool) + ".jpg"
                print(image)

            tool = Tool(tool_name=tool_name, type_of_tool=type_of_tool, owner_of_tool=tool_owner, image=image, current_shed=home_shed, 
                        description=description, condition=condition, pick_up_tool=pick_up_tool, tool_zipcode=tool_zipcode)
            if tool_name.isspace():
                return render(request, 'registration/tool_registration.html', {'form': form, 'tool_types' : TYPES_OF_TOOLS, 'conditions' : CONDITIONS, 'current_user': request.user, 'whitespace':True})
            tool.save()

            user = request.user
            user_tools = Tool.objects.filter(owner_of_tool=user)
            if not user_tools:
                user_tools = None
            alert_type = "success"
            alert_message = "Your tool was made successfully!"

            return render(request, 'registration/my_tools.html', {'user': user,  'tools': user_tools, 'alert_type': alert_type, 'alert_message': alert_message}) #TODO Change to Render user's dashboard.
        else:
            return render(request, 'registration/tool_registration.html', {'form': form, 'tool_types': TYPES_OF_TOOLS, 'conditions': CONDITIONS})
    else:
        return HttpResponse("Not POST Data.") #Debug


def remove_tool(request, tool_id):
    """
        Allows the user to deregister a tool they own.
    """
    tool = Tool.objects.get(id=tool_id)
    reservations = Reservation.objects.filter(tool=tool)
    for reservation in reservations:
        borrower = reservation.borrower
        signals.tool_deregistered.send(sender=None, tool=tool, owner=tool.owner_of_tool, requester=borrower)
        reservation.delete()
    tool.delete()
    
    alert_type = "success"
    alert_message = "Tool has been removed!"

    user = request.user
    user_tools = Tool.objects.filter(owner_of_tool=user)
    if not user_tools:
        user_tools = None
    return render(request, 'registration/my_tools.html', {'user': user,  'tools': user_tools, 'alert_type': alert_type, 'alert_message': alert_message})

def return_tool(request, reservation_id):
    """
        Sends notification to the owner of the tool ensuring that the tool has been returned IRL.
    """
    reservation = Reservation.objects.get(id=reservation_id)
    tool_to_return = reservation.tool

    tool_returned_notificaion = signals.tool_returned_check.send(sender=None, owner=tool_to_return.owner_of_tool, borrower=reservation.borrower, tool_id=tool_to_return.id, reservation_id=reservation.id)
    return HttpResponseRedirect(reverse('home:welcome', args=()))

def tool_returned(request, notification_id):
    """
        Tool has been confirmed as being returned, resets everything.
    """
    the_notification = Notification.objects.get(id=notification_id)
    tool = the_notification.tool
    reservation = the_notification.reservation

    tool.current_user_of_tool = None
    tool.save()

    reservation.delete()
    return rate_user(request, the_notification) #TODO BREAKING HERE Notification id doesn't exist.

def change_tool_availability(request, tool_id):
    """
        Allows the user to change the availability of a tool they own.
    """
    tool = Tool.objects.get(id=tool_id)

    if (tool.availability == 5):
        tool.availability = 4
    else:
        tool.availability = 5
    tool.save()

    return HttpResponseRedirect(reverse('registration:my_tools', args=()))

def add_address(request, tool_id):
    '''
    Add address is used for when a shed needs an address to find
    '''
    user = request.user
    address = request.POST['address']
    tool = Tool.objects.get(id=tool_id)
    shed = Sheds.objects.filter(shed_type=3).get(user=user)

    if (address != ''):
        user.address = address
        shed.shed_address = address
        tool.availability = 4

        user.save()
        shed.save()
        tool.save()

    return my_tools(request)

def borrow_tool(request, tool_id):
    """
        Changes current user to the borrower and sends a notification to the owner
    """
    tool = Tool.objects.get(id=tool_id)
    owner = tool.owner_of_tool
    borrower = request.user

    tool.current_user_of_tool = borrower
    if owner != borrower:
        tool_borrowed = signals.tool_borrowed.send(sender=None, owner=owner, borrower=request.user, tool_id=tool_id)
        
        tool.uses += 1
        tool.date_last_used = datetime.now()
        
        owner.times_lended += 1
        owner.save()
        
        request.user.times_borrowed += 1
        borrower.save()

    tool.save()

    return HttpResponseRedirect(reverse('home:welcome', args=()))

def cancel_reservation(request, reservation_id):
    """
        Deletes reservation for the tool
    """
    reservation = Reservation.objects.get(id=reservation_id)
    reservation.delete()

    tools = Tool.objects.filter(owner_of_tool=request.user)

    alert_type = "success"
    alert_message = "Reservation has been canceled!"

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


    return render(request, 'home/welcome.html', {'tools': tools, 'alert_type': alert_type, 'alert_message': alert_message})

def tool_request_accept(request, notification_id):
    """
        If the owner of a tool accepted a request to borrow it from their home shed, it changes the current user of the tool
        to be the requester and sends a message to the requester notifying that they're now borrowing the tool.
    """
    notification = Notification.objects.get(id=notification_id)
    tool = Tool.objects.get(id=notification.tool_id)
    borrower = notification.from_user
    owner = notification.to_user

    message = ("You have reserved " + tool.owner_of_tool.email + "'s " + tool.tool_name + ". It can be picked up at " + tool.owner_of_tool.address + ". The owner wants you to " + tool.owner_of_tool.pick_up)
    request_result = signals.request_result.send(sender=None, result=message, owner=tool.owner_of_tool, borrower=borrower)

    notification.hasBeenViewed = True
    notification.save()

    reservation = Reservation.objects.create(tool=tool, borrower=borrower, start_date=notification.start_date, end_date=notification.end_date)

    return HttpResponseRedirect(reverse('home:welcome', args=()))

def tool_request_decline(request, notification_id):
    """
        This will only be used in the home_shed area. With the request decline, a window will pop up with
        a reason why the user has declined. This will also be used for reserved times as well.
    """
    notification = Notification.objects.get(id=notification_id)
    tool_owner = request.user
    message = "I need the tool for the given time."

    message = (tool_owner.email + " has declined your request to borrow their " + notification.tool.tool_name + " because '" + message + "'.")
    request_result = signals.request_result.send(sender=None, result=message, owner=tool_owner, borrower=notification.from_user)

    notification.hasBeenViewed = True
    notification.save()

    return HttpResponseRedirect(reverse('home:welcome', args=()))

def display_tool(request, tool_id):
    """
        displays the current tools you are borrowing from the user and what tool it is
    """

    tool = Tool.objects.get(id=tool_id)
    user = request.user
    return render(request, 'registration/tool.html', {'tool': tool, 'user': user, 'tool_types': TYPES_OF_TOOLS, 'conditions': CONDITIONS})

def my_tools(request):
    user = request.user
    user_tools = Tool.objects.filter(owner_of_tool=user)
    if not user_tools:
        user_tools = None
    return render(request, 'registration/my_tools.html', {'user': user,  'tools': user_tools})

def inately_is_not_a_gun(not_a_gun):
    """
        Ensures that the tool coming in is not a gun for legailty reasons. (Note: This method is a joke.)
        @param not_a_gun: A tool that is not a gun.
        @returns: True.
    """
    if (not_a_gun):
        return True

def profile_editing(request):
    """
        Allows a user to edit their profile.
    """
    user = request.user
    return render(request, 'registration/profile.html', {'user': user, 'questions1': SECURITY_QUESTIONS_1, 'questions2': SECURITY_QUESTIONS_2, 'password' : True})  #Render profile class.

def edit_profile(request):
    """
        Edits the user info in the database.
    """
    user = request.user
    if user == request.user:
        is_user = True
    else:
        is_user = False
    tools = Tool.objects.filter(owner_of_tool=user)

    alert_type = None
    alert_message = None

    if request.method == 'POST':
        form = UserEditForm(request.POST)

        if form.is_valid():
            #user.profile_image = form.cleaned_data['profile_image']
            user.full_name = form.cleaned_data['full_name']
            user.pick_up = form.cleaned_data['pick_up']
            user.question1 = form.cleaned_data['question1']
            user.answer1 = form.cleaned_data['answer1']
            user.question2 = form.cleaned_data['question2']
            user.answer2 = form.cleaned_data['answer2']
            user.address = form.cleaned_data['address']

            shed = Sheds.objects.filter(shed_type=3).get(user=user)
            shed.shed_address = form.cleaned_data['address']
            shed.save()

            if user.answer1 == "" or user.answer1 == "None":
                user.answer1 = None

            if user.answer2 == "" or user.answer2 == "None":
                user.answer2 = None

            new_password = form.cleaned_data['new_password']
            new_password_confirm = form.cleaned_data['new_password_confirm']

            if new_password == new_password_confirm:
                user.set_password(new_password)
            else:
                return render(request, 'registration/profile.html', {'user': user, 'questions1': SECURITY_QUESTIONS_1, 'questions2': SECURITY_QUESTIONS_2, 'password' : False})

            user.save()
            home_shed = Sheds.objects.get(user=user, shed_type=3)
            home_shed.address = user.address
            home_shed.save()

            alert_type = "success"
            alert_message = "Profile changes have been saved!"

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
            alert_type = "failure"
            alert_message = "The fields were not filled out properly!"
            return render(request, 'registration/profile.html', {'user': user, 'questions1': SECURITY_QUESTIONS_1, 'questions2': SECURITY_QUESTIONS_2, 'alert_type': alert_type, 'alert_message': alert_message})
    else:
        return HttpResponse("Not POST Data.") #Debug

def tool_editing(request, tool_id):
    """
        Allows a user to edit the tool they own.
    """
    tool = Tool.objects.get(id=tool_id)
    user_sheds = Sheds.objects.filter(user=request.user)
    user = request.user

    return render(request, 'registration/tool_editing.html', {'sheds': user_sheds, 'user': user, 'tool': tool, 'tool_types': TYPES_OF_TOOLS, 'conditions': CONDITIONS, 'availability': AVAILABILITY})

def edit_tool(request, tool_id):
    """
        Edits the tool in the database.
    """
    tool = Tool.objects.get(id=tool_id)
    # blackout = Reservation.objects.filter(tool=tool, borrower=request.user)

    if request.method == 'POST':
        form = ToolEditForm(request.POST)

        if form.is_valid():
            tool.tool_name = form.cleaned_data['tool_name']
            tool.type_of_tool = form.cleaned_data['type_of_tool']
            tool.description = form.cleaned_data['description']
            tool.condition = form.cleaned_data['condition']
            tool.pick_up_tool = form.cleaned_data['pick_up_tool']
            tool.availability = form.cleaned_data['availability']
            image = form.cleaned_data['image']

            shed_id = form.cleaned_data['new_shed']
            tool.current_shed = Sheds.objects.get(pk=shed_id)

            if tool.tool_name.isspace():
                return render(request, 'registration/tool_editing.html', {'tool': tool, 'tool_types': TYPES_OF_TOOLS, 'conditions': CONDITIONS, 'availability': AVAILABILITY, 'whitespace':True})

            tool.save()
            
            reservation_list = Reservation.objects.filter(tool=tool)
            dates = request.POST['dates'].split(', ')
            if dates:
                day = timedelta(days=1)
                last_date = None
                first_date = None
                blackout = None

                for date in dates:
                    try:
                        date_element = datetime.strptime(date, '%m/%d/%y').date()
                        if date_element < datetime.today().date():
                            continue
                    except ValueError:
                        break

                    if last_date == None:
                        last_date = date_element
                        first_date = last_date
                    elif date_element != last_date + day:
                        blackout = Reservation(start_date=first_date, end_date=last_date, borrower=tool.owner_of_tool, tool=tool)
                        for reservation in reservation_list:
                            if reservation.start_date < blackout.start_date:
                                if reservation.end_date > blackout.start_date:
                                    signals.cancel_reservation.send(sender=None, shed_name=tool.current_shed.shed_name, user_to_cancel=reservation.borrower, tool=tool, user_who_canceled=request.user)
                                    reservation.delete()
                            elif reservation.start_date > blackout.start_date:
                                if reservation.start_date < blackout.end_date:
                                    signals.cancel_reservation.send(sender=None, shed_name=tool.current_shed.shed_name, user_to_cancel=reservation.borrower, tool=tool, user_who_canceled=request.user)
                                    reservation.delete()
                            else:
                                signals.cancel_reservation.send(sender=None, shed_name=tool.current_shed.shed_name, user_to_cancel=reservation.borrower, tool=tool, user_who_canceled=request.user)
                                reservation.delete()

                        blackout.save()
                        first_date = date_element
                        last_date = first_date
                    elif date_element == last_date + day:
                        last_date = date_element

                if last_date and first_date:    
                    blackout = Reservation(start_date=first_date, end_date=last_date, borrower=tool.owner_of_tool, tool=tool)
                    for reservation in reservation_list:
                        if reservation.start_date < blackout.start_date:
                            if reservation.end_date > blackout.start_date:
                                reservation.delete()
                        elif reservation.start_date > blackout.start_date:
                            if reservation.start_date < blackout.end_date:
                                reservation.delete()
                        else:
                            reservation.delete()
                    blackout.save()
            
            user = request.user
            user_tools = Tool.objects.filter(owner_of_tool=user)
            alert_type = "success"
            alert_message = "Tool has been edited!"
            if not user_tools:
                user_tools = None
            return render(request, 'registration/my_tools.html', {'user': user,  'tools': user_tools, 'alert_type': alert_type, 'alert_message': alert_message})
        else:
            user_sheds = Sheds.objects.filter(user=request.user)
            return render(request, 'registration/tool_editing.html', {'sheds': user_sheds, 'tool': tool, 'tool_types': TYPES_OF_TOOLS, 'conditions': CONDITIONS, 'availability': AVAILABILITY})
    else:
        return HttpResponseRedirect(reverse('registration:edit_tool', args=()))