from django.db import models
from django.conf import settings


class ServiceRequest(models.Model):

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("assigned", "Assigned"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    request_number = models.CharField(
        max_length=20,
        unique=True
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="service_requests"
    )

    department = models.ForeignKey(
        "departments.Department",
        on_delete=models.PROTECT,
        related_name="service_requests"
    )

    asset = models.ForeignKey(
        "assets.Asset",
        on_delete=models.PROTECT,
        related_name="service_requests",
        null=True,
        blank=True
    )

    location = models.CharField(
        max_length=150
    )

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default="medium"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_service_requests",
        null=True,
        blank=True
    )

    resolution_notes = models.TextField(
        blank=True
    )

    date_submitted = models.DateTimeField(
        auto_now_add=True
    )

    date_resolved = models.DateTimeField(
        null=True,
        blank=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-date_submitted"]

    def __str__(self):
        return f"{self.request_number} - {self.title}"