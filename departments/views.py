from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from django.db.models import Q

from accounts.access_control import (
    SupervisorRequiredMixin,
    TechnicianRequiredMixin,
)

from .forms import DepartmentForm
from .models import Department


class DepartmentListView(TechnicianRequiredMixin, ListView):

    model = Department

    template_name = "departments/list.html"

    context_object_name = "departments"

    paginate_by = 10

    def get_queryset(self):

        search = self.request.GET.get("search", "")

        queryset = Department.objects.all()

        if search:

            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(location__icontains=search) |
                Q(email__icontains=search)
            )

        return queryset.order_by("name")


class DepartmentCreateView(SupervisorRequiredMixin, CreateView):

    model = Department

    form_class = DepartmentForm

    template_name = "departments/form.html"

    success_url = reverse_lazy("departments:list")

    def form_valid(self, form):

        messages.success(
            self.request,
            "Department added successfully."
        )

        return super().form_valid(form)


class DepartmentUpdateView(SupervisorRequiredMixin, UpdateView):

    model = Department

    form_class = DepartmentForm

    template_name = "departments/form.html"

    success_url = reverse_lazy("departments:list")

    def form_valid(self, form):

        messages.success(
            self.request,
            "Department updated successfully."
        )

        return super().form_valid(form)


class DepartmentDeleteView(SupervisorRequiredMixin, DeleteView):

    model = Department

    template_name = "departments/confirm_delete.html"

    success_url = reverse_lazy("departments:list")

    def form_valid(self, form):

        messages.success(
            self.request,
            "Department deleted successfully."
        )

        return super().form_valid(form)