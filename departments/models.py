from django.db import models


class Department(models.Model):
    code = models.CharField(
        max_length=10,
        unique=True
    )

    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.TextField(
        blank=True
    )

    location = models.CharField(
        max_length=150,
        blank=True
    )

    email = models.EmailField(
        blank=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} - {self.name}"