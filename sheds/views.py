"""
    @author: Grant Gadomski, Nick Mattis, Laura Silva, Nils Sohn
"""
from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect, HttpResponse #TODO Take off HttpResponse after figuring out form error problem.
from django.core.urlresolvers import reverse
from sheds.models import Sheds, ShedMember
from registration.models import User, Tool, Reservation
from registration.models import TYPES_OF_TOOLS
from registration.models import CONDITIONS
from notification import signals
from notification.models import Notification
from sheds.forms import ReservationRequestForm, CreatePrivateShed, Search
from django.db import IntegrityError
from datetime import date
from messaging.models import Message

"""
Renders needed pages for each of the sheds
"""
def community_shed(request):
    """
        Renders the community shed page with a list of tools in the shed
    """
    user = request.user
    community_shed = Sheds.objects.filter(shed_zipcode=user.zipcode, shed_type=1)[0]
    tools = Tool.objects.filter(tool_zipcode=user.zipcode, current_shed=community_shed)
    reservation_list = Reservation.objects.filter(borrower=user)
    count_reservation = reservation_list.count()
    last_reservation = reservation_list.last()
    notification_list = Notification.objects.filter(notification_type='borrow_request', from_user=user)
    last_notification = notification_list.last()
    count_notification = notification_list.count()
    return render(request, 'sheds/community_shed.html', {'address': community_shed.shed_address, 'tools': tools,'tool_types': TYPES_OF_TOOLS, 'conditions': CONDITIONS, 'last_notification': last_notification, 'notification_list': notification_list, 'reservation_list': reservation_list, 'last_reservation': last_reservation, 'count_notification': count_notification, 'count_reservation': count_reservation})

def private_shed(request):
    """
    renders the view of all the private sheds a user knows about
    """
    user = request.user
    user_privatesheds = Sheds.objects.filter(user=user, shed_type=2)

    return render(request, 'sheds/private_shed.html', {'privatesheds': user_privatesheds})

def home_shed(request):
    """
    renders home shed
    """
    user = request.user
    shed = Sheds.objects.get(user=user, shed_type=3)

    return HttpResponseRedirect(reverse('sheds:view_shed', args=(shed.id, False, False)))

def create_privateshed(request):
    """
    renders the form that is to be filled out for the user
    """
    user = request.user
    sharezone = User.objects.filter(zipcode=user.zipcode)
    
    return render(request, 'sheds/create_privateshed.html', {'user': user, 'sharezone': sharezone})

def privateshed_create(request):
    """
    takes form data and creates a private shed with references for each memeber that was added to that shed
    """
    user = request.user
    sharezone = User.objects.filter(zipcode=user.zipcode)

    if request.method == 'POST':
        form = CreatePrivateShed(request.POST)

        if form.is_valid():
            name = form.cleaned_data['shed_name']
            address = form.cleaned_data['shed_address']
            
            if request.POST['members'] == '':
                members = []
            else:
                members = request.POST['members'].split(',')

            new_shed = Sheds(shed_name=name, shed_zipcode=user.zipcode, shed_type=2, shed_address=address)

            try:
                new_shed.save()
            except IntegrityError:
                return (render(request, 'sheds/create_privateshed.html', {'user': user, 'sharezone': sharezone, 'shed_name_not_unique': True, 'shed_address': address, 'members': members}))

            new_coordinator = ShedMember.objects.create(user=user, shed=new_shed, member_type=4)
            new_coordinator.save()

            if members:
                for member in members:
                    user = User.objects.get(email=member)
                    new_member = ShedMember.objects.create(user=user, shed=new_shed, member_type=5)
                    new_member.save()

                    if user == request.user:
                        created_shed = signals.created_new_shed.send(sender=None, shed_name=name, creator=request.user)
                    else:
                        added_to_shed = signals.added_to_shed.send(sender=None, shed_name=name, creator=request.user, person_added=user)

            return HttpResponseRedirect(reverse('sheds:private_shed', args=()))
        else:
            #return render(request, 'sheds/private_shed.html')
            return HttpResponse(form.errors)
    else:
        return HttpResponse("Not POST Data.")

def view_shed(request, shed_id, error_for_user, error_for_tool):
    """
        Renders Page to display shed information
    """
    user = request.user
    shed = Sheds.objects.get(id=shed_id)
    if shed.shed_name == user.email:
        user_tools = Tool.objects.filter(owner_of_tool=user)
        shed_tools = Tool.objects.filter(current_shed=shed)

        return render(request, 'sheds/display_shed.html', {'user': user, 'user_tools': user_tools, 'shed': shed, 'tools':shed_tools, 'error_for_tool' : error_for_tool, 'tool_types': TYPES_OF_TOOLS, 'conditions': CONDITIONS})
    else:
        sharezone = User.objects.filter(zipcode=user.zipcode)
        coordinators = User.objects.filter(shed=shed, membership__member_type=4)
        members = User.objects.filter(shed=shed, membership__member_type=5)
        user_tools = Tool.objects.filter(owner_of_tool=user)
        shed_tools = Tool.objects.filter(current_shed=shed)
        reservation_list = Reservation.objects.filter(borrower=user)
        count_reservation = reservation_list.count()
        last_reservation = reservation_list.last()
        notification_list = Notification.objects.filter(notification_type='borrow_request', from_user=user)
        last_notification = notification_list.last()
        count_notification = notification_list.count()

        return render(request, 'sheds/display_shed.html', {'user': user, 'user_tools': user_tools, 'sharezone':sharezone, 'shed': shed, 'coords': coordinators, 'members': members, 'tools':shed_tools, 'error_for_user' : error_for_user, 'error_for_tool' : error_for_tool, 'tool_types': TYPES_OF_TOOLS, 'conditions': CONDITIONS, 'last_notification': last_notification, 'notification_list': notification_list, 'reservation_list': reservation_list, 'last_reservation': last_reservation, 'count_notification': count_notification, 'count_reservation': count_reservation})

def edit_shed(request, shed_id):
    """
    edits attributes of a shed and then renders page with changes
    """
    shed = Sheds.objects.get(id=shed_id)
    if request.POST['coords'] == '':
        coordinators = []
    else:
        coordinators = request.POST['coords'].split(',')
    if request.POST['members'] == '':
        members = []
    else:
        members = request.POST['members'].split(',')
    if request.POST['tools'] == '':
        tools = []
    else:
        tools = request.POST['tools'].split(',')

    if coordinators:
        for coord in coordinators:
            user = User.objects.get(email=coord)
            old_membership = ShedMember.objects.filter(user=user, shed=shed, member_type=5)
            if old_membership:
                old_membership[0].delete()
                new_membership = ShedMember.objects.create(user=user, shed=shed, member_type=4)
            else:
                 new_membership = ShedMember.objects.create(user=user, shed=shed, member_type=4)
            new_membership.save()

    if members:
        for member in members:
            user = User.objects.get(email=member)
            coord_list = ShedMember.objects.filter(shed=shed, member_type=4)
            old_membership = ShedMember.objects.filter(user=user, shed=shed, member_type=4)
            if old_membership:
                if len(coord_list) != 1:
                    old_membership[0].delete()
                    new_membership = ShedMember.objects.create(user=user, shed=shed, member_type=5)
                else:
                    return HttpResponseRedirect(reverse('sheds:view_shed', args=(shed_id, True, False)))
            else:
                new_membership = ShedMember.objects.create(user=user, shed=shed, member_type=5)
            new_membership.save()

    if tools:
        for tool in tools:
            add_tool = Tool.objects.get(id=tool)
            if add_tool.current_user_of_tool != None:
                return HttpResponseRedirect(reverse('sheds:view_shed', args=(shed_id, False, True)))
            else:
                add_tool.current_shed = shed
                add_tool.save()
    
    return HttpResponseRedirect(reverse('sheds:view_shed', args=(shed_id, False, False)))

def remove_user_from_shed(request, shed_id, user_id):
    shed = Sheds.objects.get(id=shed_id)
    coords = User.objects.filter(shed=shed, membership__member_type=4)
    user_to_remove = User.objects.get(id=user_id)
    membership = ShedMember.objects.get(user=user_to_remove, shed=shed)

    if membership.member_type == 4: 
        if len(coords) == 1: #if they are the only coordinator left
            return HttpResponseRedirect(reverse('sheds:view_shed', args=(shed_id, True, False)))
        else:
            membership.delete()
            signals.removed_shed.send(sender=None, shed_name=shed.shed_name, user_to_remove=user_to_remove)
            return HttpResponseRedirect(reverse('sheds:view_shed', args=(shed_id, False, False)))
    else:
        membership.delete()
        signals.removed_shed.send(sender=None, shed_name=shed.shed_name, user_to_remove=user_to_remove)

        return HttpResponseRedirect(reverse('sheds:view_shed', args=(shed_id, False, False)))

def remove_tool_from_shed(request, shed_id, tool_id):
    """
    Removes a tool from a shed.
    """
    user = request.user
    shed = Sheds.objects.get(id=shed_id)
    tool = Tool.objects.get(id=tool_id)
    reserved_times = Reservation.objects.filter(tool=tool)
    if tool.current_user_of_tool != None:
        return HttpResponseRedirect(reverse('sheds:view_shed', args=(shed_id, False, False)))
    else:
        if reserved_times:
            for time in reserved_times:
                send_user = time.borrower
                time.delete()
                signals.cancel_reservation.send(sender=user, shed_name=shed.shed_name, tool=tool, user_to_cancel=send_user)
            tool.current_shed = Sheds.objects.get(user=user, shed_type=3)
        else:
            tool.current_shed = Sheds.objects.get(user=user, shed_type=3)

    tool.save()

    return HttpResponseRedirect(reverse('sheds:view_shed', args=(shed_id, False, False)))

def request_reservation(request, tool_id):
    """
        Renders reservation request form
    """
    tool = Tool.objects.get(id=tool_id)

    reservation_list = Reservation.objects.filter(tool=tool).order_by('start_date')

    form = ReservationRequestForm()
    return render(request, 'sheds/reservation_request.html', {'form': form, 'tool': tool, 'reservation_list': reservation_list})

def tool_reservation(request, tool_id):
    """
        validates and creates reservations
    """
    tool = Tool.objects.get(id=tool_id)

    if request.method == 'POST':
        form = ReservationRequestForm(request.POST)

        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']

            user = request.user
            owner = tool.owner_of_tool
            reservation_list = Reservation.objects.filter(tool=tool)
            alert_message = None

            if tool.current_shed.shed_type != 3:
                for reservation in reservation_list:
                    if start_date == None or end_date == None:
                        alert_message = "The dates are empty!"
                        return render(request, 'sheds/reservation_request.html', {'form': form, 'tool': tool, 'alert_message': alert_message})
                    elif start_date >= reservation.start_date and start_date <= reservation.end_date:
                        alert_message = "The dates overlap with other reservations!"
                        return render(request, 'sheds/reservation_request.html', {'form': form, 'tool': tool, 'alert_message': alert_message})
                    elif start_date < reservation.start_date and end_date > reservation.start_date:
                        alert_message = "The dates overlap with other reservations!"
                        return render(request, 'sheds/reservation_request.html', {'form': form, 'tool': tool, 'alert_message': alert_message})

                reservation = Reservation.objects.create(tool=tool, start_date=start_date, end_date=end_date, borrower=user)
                reservation.save()
                alert_message = "Tool has been reserved!"

            else:
                message = request.POST['message']
                borrow_request = signals.borrow_request.send(sender=None, owner=owner, requester=request.user, tool_id=tool_id, start_date=start_date, end_date=end_date, message=message)
                alert_message = "Request has been sent to the owner!"

            alert_type = "success"
            
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
            alert_message = "The dates aren't proper!"
            return render(request, 'sheds/reservation_request.html', {'form': form, 'tool': tool, 'alert_message': alert_message})
    else:
        return render(request, 'sheds/reservation_request.html', {'form': form, 'tool': tool})

def tool_list(request):
    """
        Renders the page for browsing available tools.
    """
    user = request.user
    users = User.objects.filter(zipcode=user.zipcode)
    tools = Tool.objects.filter(tool_zipcode=user.zipcode)
    reservation_list = Reservation.objects.filter(borrower=user)
    count_reservation = reservation_list.count()
    last_reservation = reservation_list.last()
    notification_list = Notification.objects.filter(notification_type='borrow_request', from_user=user)
    last_notification = notification_list.last()
    count_notification = notification_list.count()
    #return HttpResponse(last_notification.title) #Debug
    return render(request, 'sheds/tool_list.html', {'users': users, 'tools': tools,'tool_types': TYPES_OF_TOOLS,'conditions': CONDITIONS, 'last_notification': last_notification, 'notification_list': notification_list, 'reservation_list': reservation_list, 'last_reservation': last_reservation, 'count_notification': count_notification, 'count_reservation': count_reservation})

def global_search(request):
    """
        renders the page for a search.
    """
    user = request.user
    if request.method == 'POST':
        form = Search(request.POST)

        if form.is_valid():
            term = form.cleaned_data['search_term']

            if Tool.objects.filter(tool_zipcode=user.zipcode, tool_name = term):
                tools = Tool.objects.filter(tool_zipcode=user.zipcode, tool_name=term)
            else:
                tools = Tool.objects.filter(tool_zipcode=user.zipcode, tool_name__startswith = term[0])

            return render(request, 'sheds/global_search.html', {'user' : user, 'tools' : tools, 'tool_types': TYPES_OF_TOOLS,'conditions': CONDITIONS})
        else:
            #return HttpResponse(form.errors)
            return render(request, 'home/welcome.html')
    else:
        return render(request, 'home/welcome.html')