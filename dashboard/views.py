from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render

from assets.models import Asset
from departments.models import Department
from requests_app.models import ServiceRequest
from workorders.models import WorkOrder
from maintenance.models import MaintenanceSchedule
from feedback.models import Feedback


@login_required
def index(request):

    user = request.user

    context = {
        "user_role": user.role,

        # System totals
        "total_assets": Asset.objects.count(),
        "total_requests": ServiceRequest.objects.count(),
        "total_work_orders": WorkOrder.objects.count(),

        "total_technicians": request.user.__class__.objects.filter(
            role="TECHNICIAN"
        ).count(),

        "total_departments": Department.objects.count(),
        "total_maintenance": MaintenanceSchedule.objects.count(),
        "total_feedback": Feedback.objects.count(),
    }

    # ==========================================
    # ADMINISTRATOR
    # ==========================================

    if user.role == "ADMIN":

        context.update({

            "pending_requests": ServiceRequest.objects.filter(
                status="pending"
            ).count(),

            "in_progress_requests": ServiceRequest.objects.filter(
                status="in_progress"
            ).count(),

            "resolved_requests": ServiceRequest.objects.filter(
                status="resolved"
            ).count(),

        })


    # ==========================================
    # SUPERVISOR
    # ==========================================

    elif user.role == "SUPERVISOR":

        context.update({

            "pending_requests": ServiceRequest.objects.filter(
                status="pending"
            ).count(),

            "assigned_requests": ServiceRequest.objects.filter(
                status="assigned"
            ).count(),

            "in_progress_requests": ServiceRequest.objects.filter(
                status="in_progress"
            ).count(),

            "resolved_requests": ServiceRequest.objects.filter(
                status="resolved"
            ).count(),

            "department_statistics": Department.objects.annotate(
                request_count=Count("service_requests")
            ).order_by("-request_count"),

        })


    # ==========================================
    # TECHNICIAN
    # ==========================================

    elif user.role == "TECHNICIAN":

        assigned_requests = ServiceRequest.objects.filter(
            assigned_to=user
        )

        assigned_work_orders = WorkOrder.objects.filter(
            assigned_to=user
        )

        context.update({

            "my_requests": assigned_requests.count(),

            "my_pending_requests": assigned_requests.filter(
                status="pending"
            ).count(),

            "my_in_progress_requests": assigned_requests.filter(
                status="in_progress"
            ).count(),

            "my_resolved_requests": assigned_requests.filter(
                status="resolved"
            ).count(),

            "my_work_orders": assigned_work_orders.count(),

        })


    # ==========================================
    # EMPLOYEE
    # ==========================================

    elif user.role == "EMPLOYEE":

        my_requests = ServiceRequest.objects.filter(
            requester=user
        )

        context.update({

            "my_requests": my_requests.count(),

            "my_pending_requests": my_requests.filter(
                status="pending"
            ).count(),

            "my_in_progress_requests": my_requests.filter(
                status="in_progress"
            ).count(),

            "my_resolved_requests": my_requests.filter(
                status="resolved"
            ).count(),

            "my_feedback": Feedback.objects.filter(
                submitted_by=user
            ).count(),

        })


    return render(
        request,
        "dashboard/index.html",
        context
    )