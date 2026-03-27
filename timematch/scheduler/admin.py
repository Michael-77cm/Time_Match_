from django.contrib import admin
from .models import Availability, Event, Membership, Notification

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
	list_display = ("title", "code", "created_by", "finalized_datetime", "created_at")

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
	list_display = ("event", "user", "joined_at")

@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
	list_display = ("event", "user", "date", "start_time", "end_time", "status")

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
	list_display = ("user", "event", "message", "is_read", "created_at")
