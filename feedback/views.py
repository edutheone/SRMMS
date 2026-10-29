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

from .forms import FeedbackForm
from .models import Feedback


# ==========================================
# FEEDBACK VIEWS
# ==========================================

class FeedbackListView(LoginRequiredMixin, ListView):

    model = Feedback
    template_name = "feedback/feedback_list.html"
    context_object_name = "feedbacks"
    paginate_by = 10

    def get_queryset(self):

        search = self.request.GET.get("search")

        queryset = Feedback.objects.select_related(
            "service_request",
            "submitted_by",
        ).all()

        if search:
            queryset = queryset.filter(
                Q(service_request__request_number__icontains=search)
                | Q(service_request__title__icontains=search)
                | Q(submitted_by__username__icontains=search)
                | Q(comments__icontains=search)
            )

        return queryset


class FeedbackCreateView(LoginRequiredMixin, CreateView):

    model = Feedback
    form_class = FeedbackForm
    template_name = "feedback/feedback_form.html"
    success_url = reverse_lazy("feedback:list")

    def form_valid(self, form):

        response = super().form_valid(form)

        messages.success(
            self.request,
            "Feedback was submitted successfully."
        )

        return response


class FeedbackUpdateView(LoginRequiredMixin, UpdateView):

    model = Feedback
    form_class = FeedbackForm
    template_name = "feedback/feedback_form.html"
    success_url = reverse_lazy("feedback:list")

    def form_valid(self, form):

        response = super().form_valid(form)

        messages.success(
            self.request,
            "Feedback was updated successfully."
        )

        return response


class FeedbackDeleteView(LoginRequiredMixin, DeleteView):

    model = Feedback
    template_name = "feedback/feedback_confirm_delete.html"
    success_url = reverse_lazy("feedback:list")

    def form_valid(self, form):

        request_number = self.object.service_request.request_number

        response = super().form_valid(form)

        messages.success(
            self.request,
            f'Feedback for "{request_number}" was deleted successfully.'
        )

        return response