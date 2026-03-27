from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Availability, Event

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ("title",)

class JoinEventForm(forms.Form):
    code = forms.CharField(max_length=8, label="Event code")

class AvailabilityForm(forms.ModelForm):
    event = forms.ModelChoiceField(queryset=Event.objects.none())

    class Meta:
        model = Availability
        fields = ("event", "date", "start_time", "end_time", "status")
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["event"].queryset = Event.objects.filter(members__user=user).distinct()
