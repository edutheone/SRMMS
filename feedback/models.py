from django.db import models
from django.conf import settings


class Feedback(models.Model):

    RATING_CHOICES = [
        (1, "1 - Very Poor"),
        (2, "2 - Poor"),
        (3, "3 - Average"),
        (4, "4 - Good"),
        (5, "5 - Excellent"),
    ]

    service_request = models.OneToOneField(
        "requests_app.ServiceRequest",
        on_delete=models.CASCADE,
        related_name="feedback"
    )

    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="submitted_feedback"
    )

    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES
    )

    comments = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Feedback"
        verbose_name_plural = "Feedback"

    def __str__(self):
        return (
            f"{self.service_request.request_number} - "
            f"{self.rating}/5"
        )