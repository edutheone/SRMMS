from django.db import models
from django.conf import settings


class MaintenanceSchedule(models.Model):

    MAINTENANCE_TYPE_CHOICES = [
        ("preventive", "Preventive"),
        ("corrective", "Corrective"),
        ("routine", "Routine"),
        ("emergency", "Emergency"),
        ("inspection", "Inspection"),
    ]

    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("overdue", "Overdue"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    ]

    maintenance_number = models.CharField(
        max_length=20,
        unique=True
    )

    asset = models.ForeignKey(
        "assets.Asset",
        on_delete=models.PROTECT,
        related_name="maintenance_schedules"
    )

    department = models.ForeignKey(
        "departments.Department",
        on_delete=models.PROTECT,
        related_name="maintenance_schedules"
    )

    maintenance_type = models.CharField(
        max_length=20,
        choices=MAINTENANCE_TYPE_CHOICES,
        default="preventive"
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField()

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="maintenance_assignments",
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
        default="scheduled"
    )

    scheduled_date = models.DateTimeField()

    completed_date = models.DateTimeField(
        null=True,
        blank=True
    )

    maintenance_notes = models.TextField(
        blank=True
    )

    completion_notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-scheduled_date"]
        verbose_name = "Maintenance Schedule"
        verbose_name_plural = "Maintenance Schedules"

    def __str__(self):
        return f"{self.maintenance_number} - {self.title}"