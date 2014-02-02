from django.contrib import admin

from latitudeapi.models import *
# Register your models here.
admin.site.register(Location)
admin.site.register(CurrentLocation)
admin.site.register(FriendShip)