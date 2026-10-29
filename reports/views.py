from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Avg
from django.views.generic import TemplateView

from requests_app.models import ServiceRequest
from workorders.models import WorkOrder
from maintenance.models import MaintenanceSchedule
from assets.models import Asset
from departments.models import Department
from feedback.models import Feedback

from .forms import ReportFilterForm


class ReportDashboardView(LoginRequiredMixin, TemplateView):

    template_name = "reports/report_list.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        # ==========================================
        # FORM
        # ==========================================

        form = ReportFilterForm(self.request.GET or None)

        context["form"] = form

        # ==========================================
        # SERVICE REQUEST STATISTICS
        # ==========================================

        service_requests = ServiceRequest.objects.all()

        context["total_requests"] = service_requests.count()

        context["pending_requests"] = service_requests.filter(
            status="pending"
        ).count()

        context["assigned_requests"] = service_requests.filter(
            status="assigned"
        ).count()

        context["in_progress_requests"] = service_requests.filter(
            status="in_progress"
        ).count()

        context["resolved_requests"] = service_requests.filter(
            status="resolved"
        ).count()

        context["closed_requests"] = service_requests.filter(
            status="closed"
        ).count()

        # ==========================================
        # WORK ORDER STATISTICS
        # ==========================================

        work_orders = WorkOrder.objects.all()

        context["total_work_orders"] = work_orders.count()

        context["completed_work_orders"] = work_orders.filter(
            status__in=["completed", "closed"]
        ).count()

        context["pending_work_orders"] = work_orders.filter(
            status__in=["pending", "open"]
        ).count()

        # ==========================================
        # MAINTENANCE STATISTICS
        # ==========================================

        maintenance_records = MaintenanceSchedule.objects.all()

        context["total_maintenance"] = maintenance_records.count()

        context["completed_maintenance"] = maintenance_records.filter(
            status="completed"
        ).count()

        context["scheduled_maintenance"] = maintenance_records.filter(
            status="scheduled"
        ).count()

        context["in_progress_maintenance"] = maintenance_records.filter(
            status="in_progress"
        ).count()

        context["overdue_maintenance"] = maintenance_records.filter(
            status="overdue"
        ).count()

        # ==========================================
        # ASSET STATISTICS
        # ==========================================

        context["total_assets"] = Asset.objects.count()

        context["total_departments"] = Department.objects.count()

        # ==========================================
        # FEEDBACK STATISTICS
        # ==========================================

        feedback = Feedback.objects.all()

        context["total_feedback"] = feedback.count()

        context["average_rating"] = feedback.aggregate(
            average=Avg("rating")
        )["average"]

        # ==========================================
        # FEEDBACK RATING BREAKDOWN
        # ==========================================

        context["five_star"] = feedback.filter(
            rating=5
        ).count()

        context["four_star"] = feedback.filter(
            rating=4
        ).count()

        context["three_star"] = feedback.filter(
            rating=3
        ).count()

        context["two_star"] = feedback.filter(
            rating=2
        ).count()

        context["one_star"] = feedback.filter(
            rating=1
        ).count()

        # ==========================================
        # DEPARTMENT REQUEST COUNTS
        # ==========================================

        context["department_statistics"] = Department.objects.annotate(
            request_count=Count("service_requests")
        ).order_by("-request_count")

        return context