import secrets
import string
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class Event(models.Model):
title = models.CharField(max_length=200)
code = models.CharField(max_length=8, unique=True)
created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_events")
finalized_datetime = models.DateTimeField(blank=True, null=True)
created_at = models.DateTimeField(default=timezone.now)

@staticmethod
def generate_code(length=6):
alphabet = string.ascii_uppercase + string.digits
while True:
code = "".join(secrets.choice(alphabet) for _ in range(length))
if not Event.objects.filter(code=code).exists():
return code

def get_member_count(self):
return self.members.count()

def calculate_best_times(self, max_options=5):
slot_scores = {}
member_count = max(self.get_member_count(), 1)

for item in self.availabilities.exclude(status="busy"):
score_delta = 2 if item.status == "available" else 1
start = datetime.combine(item.date, item.start_time)
end = datetime.combine(item.date, item.end_time)
current = start

while current < end:
slot_scores[current] = slot_scores.get(current, 0) + score_delta
current += timedelta(minutes=30)

ranked = sorted(slot_scores.items(), key=lambda pair: pair[1], reverse=True)[:max_options]
return [
{
"datetime": dt,
"score": score,
"max_score": member_count * 2,
"match_percent": round((score / (member_count * 2)) * 100, 1),
}
for dt, score in ranked
]
class Membership(models.Model):
event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="members")
user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="event_memberships")
joined_at = models.DateTimeField(default=timezone.now)

class Meta:
constraints = [
models.UniqueConstraint(fields=["event", "user"], name="unique_event_member"),
]
class Availability(models.Model):
STATUS_CHOICES = [
("available", "Available"),
("maybe", "Maybe"),
("busy", "Busy"),
]

event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="availabilities")
user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="availabilities")
date = models.DateField()
start_time = models.TimeField()
end_time = models.TimeField()
status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="available")
created_at = models.DateTimeField(default=timezone.now)
class Notification(models.Model):
user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="notifications", null=True, blank=True)
message = models.CharField(max_length=255)
is_read = models.BooleanField(default=False)
created_at = models.DateTimeField(default=timezone.now)
