
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ADMIN = "ADMIN"
    SUPERVISOR = "SUPERVISOR"
    TECHNICIAN = "TECHNICIAN"
    EMPLOYEE = "EMPLOYEE"

    ROLE_CHOICES = [
        (ADMIN, "Administrator"),
        (SUPERVISOR, "Supervisor"),
        (TECHNICIAN, "Technician"),
        (EMPLOYEE, "Employee"),
    ]

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Enter the user's phone number.",
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=EMPLOYEE,
    )

    def __str__(self):
        return (
            f"{self.get_full_name() or self.username} "
            f"({self.get_role_display()})"
        )
