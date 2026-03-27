from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AvailabilityForm, EventForm, JoinEventForm, SignUpForm
from .models import Event, Membership, Notification

def home(request):
	return render(request, "scheduler/home.html")

def signup_view(request):
	if request.user.is_authenticated:
		return redirect("create_event")
	if request.method == "POST":
		form = SignUpForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			return redirect("create_event")
	else:
		form = SignUpForm()
	return render(request, "registration/signup.html", {"form": form})

@login_required
def create_event(request):
	if request.method == "POST":
		form = EventForm(request.POST)
		if form.is_valid():
			event = form.save(commit=False)
			event.created_by = request.user
			event.code = Event.generate_code()
			event.save()
			Membership.objects.get_or_create(event=event, user=request.user)
			Notification.objects.create(
				user=request.user,
				event=event,
				message=f"You've joined event '{event.title}'.",
			)
			messages.success(request, f"Event created with code: {event.code}")
			return redirect("event_overview")
	else:
		form = EventForm()
	events = Event.objects.filter(members__user=request.user).distinct().order_by("-created_at")
	return render(request, "scheduler/create_event.html", {"form": form, "events": events})

@login_required
def join_event(request):
	if request.method == "POST":
		form = JoinEventForm(request.POST)
		if form.is_valid():
			code = form.cleaned_data["code"].strip().upper()
			event = Event.objects.filter(code=code).first()
			if not event:
				messages.error(request, "Invalid event code.")
			else:
				membership, created = Membership.objects.get_or_create(event=event, user=request.user)
				if created:
					Notification.objects.create(
						user=request.user,
						event=event,
						message=f"You've joined event '{event.title}'.",
					)
					for member in User.objects.filter(event_memberships__event=event).exclude(id=request.user.id).distinct():
						Notification.objects.create(
							user=member,
							event=event,
							message=f"{request.user.username} has joined '{event.title}'.",
						)
				messages.success(request, f"Joined event: {event.title}")
				return redirect("availability_input")
	else:
		form = JoinEventForm()
	return render(request, "scheduler/join_event.html", {"form": form})

@login_required
def availability_input(request):
	if request.method == "POST":
		form = AvailabilityForm(request.POST, user=request.user)
		if form.is_valid():
			availability = form.save(commit=False)
			availability.user = request.user
			availability.save()

			for member in User.objects.filter(event_memberships__event=availability.event).exclude(id=request.user.id).distinct():
				Notification.objects.create(
					user=member,
					event=availability.event,
					message=f"New availability added for '{availability.event.title}'.",
				)

			messages.success(request, "Availability added.")
			return redirect("event_overview")
	else:
		form = AvailabilityForm(user=request.user)
	return render(request, "scheduler/availability_input.html", {"form": form})

@login_required
def event_overview(request):
	events = Event.objects.filter(members__user=request.user).distinct().order_by("-created_at")
	selected_event = None
	best_time = None
	other_options = []

	event_id = request.GET.get("event_id")
	if event_id:
		selected_event = get_object_or_404(events, id=event_id)
	elif events.exists():
		selected_event = events.first()

	if selected_event:
		options = selected_event.calculate_best_times(max_options=5)
		if options:
			best_time = options[0]
			other_options = options[1:]

	if request.method == "POST" and request.POST.get("finalize") and best_time:
		selected_event.finalized_datetime = best_time["datetime"]
		selected_event.save(update_fields=["finalized_datetime"])

		for member in User.objects.filter(event_memberships__event=selected_event).distinct():
			Notification.objects.create(
				user=member,
				event=selected_event,
				message=(
					f"Event time finalized for '{selected_event.title}' at "
					f"{selected_event.finalized_datetime.strftime('%b %d, %Y %I:%M %p')}."
				),
			)
		messages.success(request, "Event finalized.")
		return redirect(f"/dashboard/event-overview/?event_id={selected_event.id}")

	return render(
		request,
		"scheduler/event_overview.html",
		{
			"events": events,
			"selected_event": selected_event,
			"best_time": best_time,
			"other_options": other_options,
		},
	)

@login_required
def notification_panel(request):
	if request.method == "POST" and request.POST.get("mark_read"):
		Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
		messages.success(request, "Notifications marked as read.")
		return redirect("notification_panel")

	notifications = Notification.objects.filter(user=request.user).order_by("-created_at")
	return render(request, "scheduler/notification_panel.html", {"notifications": notifications})
