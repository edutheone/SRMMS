
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)

from accounts.access_control import (
    SupervisorRequiredMixin,
    EmployeeRequiredMixin,
)

from notifications_app.models import Notification

from .forms import ServiceRequestForm
from .models import ServiceRequest


# ==========================================
# SERVICE REQUEST LIST
# ==========================================

class ServiceRequestListView(EmployeeRequiredMixin, ListView):

    model = ServiceRequest
    template_name = "requests/service_request_list.html"
    context_object_name = "service_requests"
    paginate_by = 10

    def get_queryset(self):

        search = self.request.GET.get("search", "")
        user = self.request.user

        queryset = ServiceRequest.objects.select_related(
            "requester",
            "department",
            "asset",
            "assigned_to",
        )

        # ==========================================
        # ROLE-BASED DATA ACCESS
        # ==========================================

        if user.role in ["ADMIN", "SUPERVISOR"]:

            queryset = queryset.all()

        elif user.role == "TECHNICIAN":

            queryset = queryset.filter(
                assigned_to=user
            )

        elif user.role == "EMPLOYEE":

            queryset = queryset.filter(
                requester=user
            )

        # ==========================================
        # SEARCH
        # ==========================================

        if search:

            queryset = queryset.filter(
                Q(request_number__icontains=search)
                | Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(location__icontains=search)
                | Q(department__name__icontains=search)
                | Q(asset__name__icontains=search)
                | Q(asset__asset_tag__icontains=search)
            )

        return queryset


# ==========================================
# CREATE SERVICE REQUEST
# ==========================================

class ServiceRequestCreateView(EmployeeRequiredMixin, CreateView):

    model = ServiceRequest
    form_class = ServiceRequestForm
    template_name = "requests/service_request_form.html"
    success_url = reverse_lazy("requests_app:list")

    def get_form_kwargs(self):

        kwargs = super().get_form_kwargs()

        # Send logged-in user to the form
        kwargs["user"] = self.request.user

        return kwargs

    def form_valid(self, form):

        # ==========================================
        # EMPLOYEE
        # ==========================================

        if self.request.user.role == "EMPLOYEE":

            # Automatically set the requester
            form.instance.requester = self.request.user

            # New requests must start as Pending
            form.instance.status = "pending"

            # Employee cannot assign a technician
            form.instance.assigned_to = None

            # No resolution information at creation
            form.instance.resolution_notes = ""
            form.instance.date_resolved = None

        # Save the service request first
        response = super().form_valid(form)

        # ==========================================
        # NOTIFY ADMINISTRATORS AND SUPERVISORS
        # ==========================================

        if self.request.user.role == "EMPLOYEE":

            recipients = self.request.user.__class__.objects.filter(
                role__in=["ADMIN", "SUPERVISOR"],
                is_active=True,
            )

            notifications = []

            for recipient in recipients:

                notifications.append(
                    Notification(
                        recipient=recipient,
                        notification_type="service_request",
                        title="New Service Request Submitted",
                        message=(
                            f'{self.object.requester.get_full_name() or self.object.requester.username} '
                            f'has submitted a new service request.\n\n'
                            f'Request Number: {self.object.request_number}\n'
                            f'Title: {self.object.title}\n'
                            f'Department: {self.object.department.name}\n'
                            f'Priority: {self.object.get_priority_display()}\n'
                            f'Location: {self.object.location}\n'
                            f'Status: {self.object.get_status_display()}'
                        ),
                        priority=self.object.priority,
                    )
                )

            # Save all notifications
            Notification.objects.bulk_create(notifications)

        # ==========================================
        # SUCCESS MESSAGE
        # ==========================================

        messages.success(
            self.request,
            f'Service request "{self.object.request_number}" was created successfully.'
        )

        return response


# ==========================================
# UPDATE SERVICE REQUEST
# ==========================================

class ServiceRequestUpdateView(EmployeeRequiredMixin, UpdateView):

    model = ServiceRequest
    form_class = ServiceRequestForm
    template_name = "requests/service_request_form.html"
    success_url = reverse_lazy("requests_app:list")

    def get_queryset(self):

        user = self.request.user

        # ==========================================
        # ADMIN
        # ==========================================

        if user.role == "ADMIN":

            return ServiceRequest.objects.all()

        # ==========================================
        # SUPERVISOR
        # ==========================================

        if user.role == "SUPERVISOR":

            return ServiceRequest.objects.all()

        # ==========================================
        # TECHNICIAN
        # ==========================================

        if user.role == "TECHNICIAN":

            return ServiceRequest.objects.filter(
                assigned_to=user
            )

        # ==========================================
        # EMPLOYEE
        # ==========================================

        if user.role == "EMPLOYEE":

            return ServiceRequest.objects.filter(
                requester=user
            )

        return ServiceRequest.objects.none()

    def get_form_kwargs(self):

        kwargs = super().get_form_kwargs()

        kwargs["user"] = self.request.user

        return kwargs

    def form_valid(self, form):

        user = self.request.user

        # ==========================================
        # TECHNICIAN
        # ==========================================

        if user.role == "TECHNICIAN":

            form.instance.assigned_to = self.object.assigned_to
            form.instance.requester = self.object.requester

        # ==========================================
        # EMPLOYEE
        # ==========================================

        elif user.role == "EMPLOYEE":

            form.instance.requester = self.object.requester

            form.instance.assigned_to = self.object.assigned_to

            form.instance.status = self.object.status

            form.instance.resolution_notes = self.object.resolution_notes
            form.instance.date_resolved = self.object.date_resolved

        response = super().form_valid(form)

        messages.success(
            self.request,
            f'Service request "{self.object.request_number}" was updated successfully.'
        )

        return response


# ==========================================
# DELETE SERVICE REQUEST
# ==========================================

class ServiceRequestDeleteView(SupervisorRequiredMixin, DeleteView):

    model = ServiceRequest
    template_name = "requests/service_request_confirm_delete.html"
    success_url = reverse_lazy("requests_app:list")

    def get_queryset(self):

        user = self.request.user

        if user.role == "ADMIN":

            return ServiceRequest.objects.all()

        if user.role == "SUPERVISOR":

            return ServiceRequest.objects.all()

        return ServiceRequest.objects.none()

    def form_valid(self, form):

        request_number = self.object.request_number

        response = super().form_valid(form)

        messages.success(
            self.request,
            f'Service request "{request_number}" was deleted successfully.'
        )

        return response