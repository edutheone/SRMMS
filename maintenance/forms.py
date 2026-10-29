from django import forms
from .models import MaintenanceSchedule


class MaintenanceScheduleForm(forms.ModelForm):

    class Meta:
        model = MaintenanceSchedule

        fields = [
            "maintenance_number",
            "asset",
            "department",
            "maintenance_type",
            "title",
            "description",
            "assigned_to",
            "location",
            "priority",
            "status",
            "scheduled_date",
            "completed_date",
            "maintenance_notes",
            "completion_notes",
        ]

        widgets = {

            "maintenance_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter maintenance number",
                }
            ),

            "asset": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "department": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "maintenance_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter maintenance title",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe the maintenance required...",
                }
            ),

            "assigned_to": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter maintenance location",
                }
            ),

            "priority": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "scheduled_date": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),

            "completed_date": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),

            "maintenance_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Enter maintenance notes...",
                }
            ),

            "completion_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Enter completion notes...",
                }
            ),
        }