from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, View
from django.http import JsonResponse

from .models import Notification


class NotificationListView(LoginRequiredMixin, ListView):

    model = Notification
    template_name = "notifications/notification_list.html"
    context_object_name = "notifications"
    paginate_by = 10

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).order_by("-created_at")


class NotificationMarkReadView(LoginRequiredMixin, View):

    def post(self, request, pk):

        notification = get_object_or_404(
            Notification,
            pk=pk,
            recipient=request.user
        )

        notification.is_read = True
        notification.save(update_fields=["is_read", "updated_at"])

        return redirect("notifications_app:list")


class NotificationMarkAllReadView(LoginRequiredMixin, View):

    def post(self, request):

        Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True)

        messages.success(
            request,
            "All notifications have been marked as read."
        )

        return redirect("notifications_app:list")
    
    
class NotificationPopupView(LoginRequiredMixin, View):

    def get(self, request):
        notifications = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).order_by("-created_at")[:5]

        data = []

        for notification in notifications:
            data.append({
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "priority": notification.priority,
                "created_at": notification.created_at.strftime(
                    "%d %b %Y, %H:%M"
                ),
            })

        return JsonResponse({
            "notifications": data
        })    