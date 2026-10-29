from django.db import models
from django.conf import settings


class WorkOrder(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("assigned", "Assigned"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    # Work Order Number
    work_order_number = models.CharField(
        max_length=20,
        unique=True
    )

    # Basic information
    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    # Related Service Request
    service_request = models.ForeignKey(
        "requests_app.ServiceRequest",
        on_delete=models.PROTECT,
        related_name="work_orders",
        null=True,
        blank=True
    )

    # Related Asset
    asset = models.ForeignKey(
        "assets.Asset",
        on_delete=models.PROTECT,
        related_name="work_orders",
        null=True,
        blank=True
    )

    # Department responsible for the work
    department = models.ForeignKey(
        "departments.Department",
        on_delete=models.PROTECT,
        related_name="work_orders"
    )

    # Technician assigned to the work
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="work_orders",
        null=True,
        blank=True
    )

    # Location where the work will be performed
    location = models.CharField(
        max_length=150
    )

    # Priority
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="medium"
    )

    # Work order status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    # Work performed
    work_description = models.TextField(
        blank=True
    )

    # Final notes after completing the work
    completion_notes = models.TextField(
        blank=True
    )

    # Scheduled date
    scheduled_date = models.DateTimeField(
        null=True,
        blank=True
    )

    # Actual completion date
    completed_date = models.DateTimeField(
        null=True,
        blank=True
    )

    # System timestamps
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.work_order_number} - {self.title}"