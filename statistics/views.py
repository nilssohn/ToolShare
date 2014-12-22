"""
    @author Grant Gadomski
"""
from django.shortcuts import render

from registration.models import User, Tool
from datetime import date, datetime

def show_user_statistics(request):
    """
        Renders a page showing the most active borrowers and lenders in the share zone.
    """
    user = request.user
    zipcode = user.zipcode
    
    users = User.objects.filter(zipcode=zipcode)
    
    times_lended = users.order_by('-times_lended')
    times_borrowed = users.order_by('-times_borrowed')
    times_lended = list(times_lended)
    times_borrowed = list(times_borrowed)
    
    top_times_lended = []
    lended_index = 0
    lended_length = len(times_lended)
    if (lended_length > 5):
        lended_length = 5
        
    while lended_index < lended_length:
        top_lended = times_lended[lended_index]
        top_times_lended.append(top_lended)
        lended_index += 1
        
    top_times_borrowed = []
    borrowed_index = 0
    borrowed_length = len(times_borrowed)
    if (borrowed_length > 5):
        borrowed_length = 5
        
    while borrowed_index < borrowed_length:
        top_borrowed = times_borrowed[borrowed_index]
        top_times_borrowed.append(top_borrowed)
        borrowed_index += 1
        
    if len(times_lended) == 0:
        times_lended = None
    if len(times_borrowed) == 0:
        times_borrowed = None
    
    return render(request, 'statistics/user_statistics.html', {'times_lended': top_times_lended, 'times_borrowed': top_times_borrowed})
    
def show_tool_statistics(request):
    """
        Renders a page showing the most borrowed tools and the most recently borrowed tools.
    """
    user = request.user
    zipcode = user.zipcode
    
    tools = Tool.objects.filter(tool_zipcode=zipcode)
    
    times_borrowed = tools.order_by('-uses')
    recently_borrowed = tools.order_by('date_last_used')
    times_borrowed = list(times_borrowed)
    recently_borrowed = list(recently_borrowed)
    
    top_times_borrowed = []
    borrowed_index = 0
    borrowed_length = len(times_borrowed)
    if borrowed_length > 5:
        borrowed_length = 5
        
    while borrowed_index < borrowed_length:
        top_borrowed = times_borrowed[borrowed_index]
        top_times_borrowed.append(top_borrowed)
        borrowed_index += 1
        
    top_recently_borrowed = []
    recent_index = 0
    recent_length = len(recently_borrowed)
    if recent_length > 5:
        recent_length = 5
        
    while recent_index < recent_length:
        recent_borrowed = recently_borrowed[recent_index]
        top_recently_borrowed.append(recent_borrowed)
        recent_index += 1
        
    if len(times_borrowed) == 0:
        top_times_borrowed = None
    if len(recently_borrowed) == 0:
        top_recently_borrowed = None
    
    return render(request, 'statistics/tool_statistics.html', {'times_borrowed': top_times_borrowed, 'recently_borrowed': top_recently_borrowed})
    
def show_user_ratings(request):
    '''
        Will show the user ratings according to how many 
        thumbs up and thumbs down they have
    '''
    user = request.user
    zipcode = user.zipcode
    
    users = User.objects.filter(zipcode=zipcode)
    thumbs_up = users.order_by('-thumbs_up')
    thumbs_down = users.order_by('-thumbs_down')
    thumbs_up = list(thumbs_up)
    thumbs_down = list(thumbs_down)
    
    top_thumbs_up = []
    up_index = 0
    up_length = len(thumbs_up)
    if up_length > 5:
        up_length = 5
        
    while up_index < up_length:
        top_up = thumbs_up[up_index]
        top_thumbs_up.append(top_up)
        up_index += 1
        
    top_thumbs_down = []
    down_index = 0
    down_length = len(thumbs_down)
    if down_length > 5:
        down_length = 5
        
    while down_index < down_length:
        top_down = thumbs_down[down_index]
        top_thumbs_down.append(top_down)
        down_index += 1
        
    if len(top_thumbs_up) == 0:
        top_thumbs_up = None
    if len(top_thumbs_down) == 0:
        top_thumbs_down = None
        
    return render(request, 'statistics/user_ratings.html', {'thumbs_up': top_thumbs_up, 'thumbs_down': top_thumbs_down})