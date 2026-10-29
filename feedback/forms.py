from django import forms
from .models import Feedback


class FeedbackForm(forms.ModelForm):

    class Meta:
        model = Feedback

        fields = [
            "service_request",
            "submitted_by",
            "rating",
            "comments",
        ]

        widgets = {

            "service_request": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "submitted_by": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "rating": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "comments": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Tell us about your experience...",
                }
            ),
        }