from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)

from accounts.access_control import (
    SupervisorRequiredMixin,
    TechnicianRequiredMixin,
)

from requests_app.models import ServiceRequest
from notifications_app.models import Notification

from .forms import WorkOrderForm
from .models import WorkOrder


# =========================================================
# WORK ORDER LIST
# =========================================================

class WorkOrderListView(TechnicianRequiredMixin, ListView):

    model = WorkOrder
    template_name = "workorders/work_order_list.html"
    context_object_name = "work_orders"
    paginate_by = 10

    def get_queryset(self):

        search = self.request.GET.get("search", "")

        queryset = WorkOrder.objects.select_related(
            "service_request",
            "asset",
            "department",
            "assigned_to",
        )

        user = self.request.user

        # -------------------------------------------------
        # ADMIN + SUPERVISOR
        # Can see all work orders
        # -------------------------------------------------

        if user.role in ["ADMIN", "SUPERVISOR"]:

            queryset = queryset.all()

        # -------------------------------------------------
        # TECHNICIAN
        # Can only see work orders assigned to them
        # -------------------------------------------------

        elif user.role == "TECHNICIAN":

            queryset = queryset.filter(
                assigned_to=user
            )

        # -------------------------------------------------
        # SEARCH
        # -------------------------------------------------

        if search:

            queryset = queryset.filter(
                Q(work_order_number__icontains=search)
                | Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(location__icontains=search)
                | Q(
                    service_request__request_number__icontains=search
                )
                | Q(asset__name__icontains=search)
                | Q(asset__asset_tag__icontains=search)
                | Q(department__name__icontains=search)
                | Q(assigned_to__username__icontains=search)
            )

        return queryset.order_by("-id")


# =========================================================
# CREATE WORK ORDER
# =========================================================

class WorkOrderCreateView(SupervisorRequiredMixin, CreateView):

    model = WorkOrder
    form_class = WorkOrderForm
    template_name = "workorders/work_order_form.html"
    success_url = reverse_lazy("workorders:list")

    def get_service_request(self):

        request_id = self.request.GET.get("service_request")

        if not request_id:
            return None

        return get_object_or_404(
            ServiceRequest,
            pk=request_id
        )

    def get_form_kwargs(self):

        kwargs = super().get_form_kwargs()

        # Pass logged-in user to WorkOrderForm
        kwargs["user"] = self.request.user

        return kwargs

    def get_initial(self):

        initial = super().get_initial()

        service_request = self.get_service_request()

        if service_request:

            initial.update({
                "service_request": service_request,
                "title": service_request.title,
                "description": service_request.description,
                "asset": service_request.asset,
                "department": service_request.department,
                "location": service_request.location,
                "priority": service_request.priority,
                "status": "assigned",
            })

        return initial

    def form_valid(self, form):

        service_request = self.get_service_request()

        if not service_request:

            form.add_error(
                None,
                "A Service Request must be selected before creating a Work Order."
            )

            return self.form_invalid(form)

        # -------------------------------------------------
        # COPY INFORMATION FROM SERVICE REQUEST
        # -------------------------------------------------

        form.instance.service_request = service_request
        form.instance.title = service_request.title
        form.instance.description = service_request.description
        form.instance.asset = service_request.asset
        form.instance.department = service_request.department
        form.instance.location = service_request.location
        form.instance.priority = service_request.priority

        # -------------------------------------------------
        # WORK ORDER STATUS
        # -------------------------------------------------

        form.instance.status = "assigned"

        # -------------------------------------------------
        # TECHNICIAN
        # -------------------------------------------------

        if not form.cleaned_data.get("assigned_to"):

            form.add_error(
                "assigned_to",
                "Please select a technician."
            )

            return self.form_invalid(form)

        # -------------------------------------------------
        # SAVE WORK ORDER
        # -------------------------------------------------

        response = super().form_valid(form)

        # -------------------------------------------------
        # UPDATE SERVICE REQUEST
        # -------------------------------------------------

        service_request.assigned_to = form.instance.assigned_to
        service_request.status = "assigned"

        service_request.save(
            update_fields=[
                "assigned_to",
                "status",
                "updated_at",
            ]
        )

        # -------------------------------------------------
        # NOTIFY ASSIGNED TECHNICIAN
        # -------------------------------------------------

        technician = self.object.assigned_to

        Notification.objects.create(
            recipient=technician,
            notification_type="work_order",
            title="New Work Order Assigned",
            message=(
                "You have been assigned a new work order.\n\n"
                f"Work Order Number: "
                f"{self.object.work_order_number}\n"
                f"Title: {self.object.title}\n"
                f"Service Request: "
                f"{service_request.request_number}\n"
                f"Department: "
                f"{self.object.department.name}\n"
                f"Location: {self.object.location}\n"
                f"Priority: "
                f"{self.object.get_priority_display()}\n"
                f"Status: "
                f"{self.object.get_status_display()}"
            ),
            priority=self.object.priority,
        )

        # -------------------------------------------------
        # SUCCESS MESSAGE
        # -------------------------------------------------

        messages.success(
            self.request,
            f'Work order "{self.object.work_order_number}" '
            f'was created successfully and assigned to '
            f'{self.object.assigned_to.get_full_name() or self.object.assigned_to.username}.'
        )

        return response


# =========================================================
# UPDATE WORK ORDER
# =========================================================

class WorkOrderUpdateView(TechnicianRequiredMixin, UpdateView):

    model = WorkOrder
    form_class = WorkOrderForm
    template_name = "workorders/work_order_form.html"
    success_url = reverse_lazy("workorders:list")

    def get_queryset(self):

        user = self.request.user

        # -------------------------------------------------
        # ADMIN + SUPERVISOR
        # Can edit all work orders
        # -------------------------------------------------

        if user.role in ["ADMIN", "SUPERVISOR"]:

            return WorkOrder.objects.all()

        # -------------------------------------------------
        # TECHNICIAN
        # Can only edit work orders assigned to them
        # -------------------------------------------------

        if user.role == "TECHNICIAN":

            return WorkOrder.objects.filter(
                assigned_to=user
            )

        # -------------------------------------------------
        # OTHER USERS
        # -------------------------------------------------

        return WorkOrder.objects.none()

    def get_form_kwargs(self):

        kwargs = super().get_form_kwargs()

        # Pass logged-in user to WorkOrderForm
        kwargs["user"] = self.request.user

        return kwargs

    def form_valid(self, form):

        # -------------------------------------------------
        # REMEMBER OLD STATUS
        # -------------------------------------------------

        old_status = self.object.status

        # -------------------------------------------------
        # GET NEW STATUS FROM FORM
        # -------------------------------------------------

        new_status = form.cleaned_data.get("status")

        # -------------------------------------------------
        # SAVE THE WORK ORDER
        # -------------------------------------------------

        response = super().form_valid(form)

        # -------------------------------------------------
        # CHECK IF WORK ORDER HAS JUST BEEN COMPLETED
        # -------------------------------------------------

        if (
            old_status != "completed"
            and new_status == "completed"
        ):

            service_request = self.object.service_request

            # -------------------------------------------------
            # SERVICE REQUEST NUMBER
            # -------------------------------------------------

            if service_request:

                service_request_number = (
                    service_request.request_number
                )

            else:

                service_request_number = "N/A"

            # -------------------------------------------------
            # TECHNICIAN NAME
            # -------------------------------------------------

            if self.object.assigned_to:

                technician_name = (
                    self.object.assigned_to.get_full_name()
                    or self.object.assigned_to.username
                )

            else:

                technician_name = "Not assigned"

            # -------------------------------------------------
            # COMPLETION NOTES
            # -------------------------------------------------

            completion_notes = (
                self.object.completion_notes
                or "No completion notes provided."
            )

            # -------------------------------------------------
            # NOTIFY ORIGINAL EMPLOYEE
            # -------------------------------------------------

            if service_request and service_request.requester:

                Notification.objects.create(
                    recipient=service_request.requester,
                    notification_type="work_order",
                    title="Work Order Completed",
                    message=(
                        "Your service request has been completed.\n\n"
                        f"Work Order Number: "
                        f"{self.object.work_order_number}\n"
                        f"Title: {self.object.title}\n"
                        f"Service Request: "
                        f"{service_request_number}\n"
                        f"Department: "
                        f"{self.object.department.name}\n"
                        f"Location: {self.object.location}\n"
                        f"Status: "
                        f"{self.object.get_status_display()}\n\n"
                        f"Completion Notes: "
                        f"{completion_notes}"
                    ),
                    priority=self.object.priority,
                )

            # -------------------------------------------------
            # NOTIFY ADMINISTRATORS AND SUPERVISORS
            # -------------------------------------------------

            recipients = self.request.user.__class__.objects.filter(
                role__in=[
                    "ADMIN",
                    "SUPERVISOR",
                ],
                is_active=True,
            )

            notifications = []

            for recipient in recipients:

                notifications.append(
                    Notification(
                        recipient=recipient,
                        notification_type="work_order",
                        title="Work Order Completed",
                        message=(
                            f'Work order '
                            f'"{self.object.work_order_number}" '
                            f'has been completed.\n\n'
                            f"Title: {self.object.title}\n"
                            f"Service Request: "
                            f"{service_request_number}\n"
                            f"Technician: "
                            f"{technician_name}\n"
                            f"Department: "
                            f"{self.object.department.name}\n"
                            f"Location: "
                            f"{self.object.location}\n"
                            f"Priority: "
                            f"{self.object.get_priority_display()}\n"
                            f"Status: "
                            f"{self.object.get_status_display()}"
                        ),
                        priority=self.object.priority,
                    )
                )

            if notifications:

                Notification.objects.bulk_create(
                    notifications
                )

        # -------------------------------------------------
        # SUCCESS MESSAGE
        # -------------------------------------------------

        messages.success(
            self.request,
            f'Work order "{self.object.work_order_number}" '
            f'was updated successfully.'
        )

        return response


# =========================================================
# DELETE WORK ORDER
# =========================================================

class WorkOrderDeleteView(SupervisorRequiredMixin, DeleteView):

    model = WorkOrder
    template_name = "workorders/work_order_confirm_delete.html"
    success_url = reverse_lazy("workorders:list")

    def form_valid(self, form):

        work_order_number = self.object.work_order_number

        response = super().form_valid(form)

        messages.success(
            self.request,
            f'Work order "{work_order_number}" '
            f'was deleted successfully.'
        )

        return response