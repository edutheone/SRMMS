from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .forms import MaintenanceScheduleForm
from .models import MaintenanceSchedule


# ==========================================
# MAINTENANCE SCHEDULE VIEWS
# ==========================================


class MaintenanceScheduleListView(LoginRequiredMixin, ListView):

    model = MaintenanceSchedule
    template_name = "maintenance/maintenance_list.html"
    context_object_name = "maintenance_schedules"
    paginate_by = 10

    def get_queryset(self):

        search = self.request.GET.get("search")

        queryset = MaintenanceSchedule.objects.select_related(
            "asset",
            "department",
            "assigned_to",
        ).all()

        if search:
            queryset = queryset.filter(
                Q(maintenance_number__icontains=search)
                | Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(location__icontains=search)
                | Q(asset__name__icontains=search)
                | Q(asset__asset_tag__icontains=search)
                | Q(department__name__icontains=search)
                | Q(assigned_to__username__icontains=search)
            )

        return queryset


class MaintenanceScheduleCreateView(LoginRequiredMixin, CreateView):

    model = MaintenanceSchedule
    form_class = MaintenanceScheduleForm
    template_name = "maintenance/maintenance_form.html"
    success_url = reverse_lazy("maintenance:list")

    def form_valid(self, form):

        response = super().form_valid(form)

        messages.success(
            self.request,
            f'Maintenance schedule "{self.object.maintenance_number}" '
            f'was created successfully.'
        )

        return response


class MaintenanceScheduleUpdateView(LoginRequiredMixin, UpdateView):

    model = MaintenanceSchedule
    form_class = MaintenanceScheduleForm
    template_name = "maintenance/maintenance_form.html"
    success_url = reverse_lazy("maintenance:list")

    def form_valid(self, form):

        response = super().form_valid(form)

        messages.success(
            self.request,
            f'Maintenance schedule "{self.object.maintenance_number}" '
            f'was updated successfully.'
        )

        return response


class MaintenanceScheduleDeleteView(LoginRequiredMixin, DeleteView):

    model = MaintenanceSchedule
    template_name = "maintenance/maintenance_confirm_delete.html"
    success_url = reverse_lazy("maintenance:list")

    def form_valid(self, form):

        maintenance_number = self.object.maintenance_number

        response = super().form_valid(form)

        messages.success(
            self.request,
            f'Maintenance schedule "{maintenance_number}" '
            f'was deleted successfully.'
        )

        return response