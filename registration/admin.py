from django.contrib import admin
from registration.models import User, Tool, ShareZone
from sheds.models import Sheds

admin.site.register(User)
admin.site.register(Tool)
admin.site.register(ShareZone)
admin.site.register(Sheds)