from django import forms


class ReportFilterForm(forms.Form):

    REPORT_TYPE_CHOICES = [
        ("service_requests", "Service Requests"),
        ("work_orders", "Work Orders"),
        ("maintenance", "Maintenance"),
        ("assets", "Assets"),
        ("feedback", "Feedback"),
    ]

    report_type = forms.ChoiceField(
        choices=REPORT_TYPE_CHOICES,
        required=True,
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        )
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            }
        )
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            }
        )
    )

    status = forms.ChoiceField(
        required=False,
        choices=[
            ("", "All Statuses"),
            ("pending", "Pending"),
            ("assigned", "Assigned"),
            ("in_progress", "In Progress"),
            ("resolved", "Resolved"),
            ("closed", "Closed"),
        ],
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        )
    )

    priority = forms.ChoiceField(
        required=False,
        choices=[
            ("", "All Priorities"),
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
            ("critical", "Critical"),
        ],
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        )
    )

    def clean(self):
        cleaned_data = super().clean()

        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")

        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError(
                "The start date cannot be later than the end date."
            )

        return cleaned_data