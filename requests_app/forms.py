from django import forms

from .models import ServiceRequest


class ServiceRequestForm(forms.ModelForm):

    class Meta:
        model = ServiceRequest

        fields = [
            "request_number",
            "title",
            "description",
            "requester",
            "department",
            "asset",
            "location",
            "priority",
            "status",
            "assigned_to",
            "resolution_notes",
            "date_resolved",
        ]

        widgets = {

            "request_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter request number",
                }
            ),

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter service request title",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe the problem or service required...",
                }
            ),

            "requester": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "department": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "asset": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter location",
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

            "assigned_to": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "resolution_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Enter resolution notes if applicable...",
                }
            ),

            "date_resolved": forms.DateTimeInput(
                attrs={
                    "class": "form-control",
                    "type": "datetime-local",
                }
            ),
        }

    # ==========================================
    # ROLE-BASED FORM CONTROL
    # ==========================================

    def __init__(self, *args, **kwargs):

        user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        # ------------------------------------------
        # EMPLOYEE
        # ------------------------------------------

        if user and user.role == "EMPLOYEE":

            # Employee should not choose the requester.
            self.fields.pop("requester", None)

            # Employee should not assign a technician.
            self.fields.pop("assigned_to", None)

            # Employee should not change the status.
            self.fields.pop("status", None)

            # Employee should not enter resolution information.
            self.fields.pop("resolution_notes", None)
            self.fields.pop("date_resolved", None)

        # ------------------------------------------
        # TECHNICIAN
        # ------------------------------------------

        elif user and user.role == "TECHNICIAN":

            # Technician should not change the requester.
            self.fields.pop("requester", None)

            # Technician should not assign the request.
            self.fields.pop("assigned_to", None)

        # ------------------------------------------
        # SUPERVISOR
        # ------------------------------------------

        elif user and user.role == "SUPERVISOR":

            # Supervisor can manage requests.
            pass

        # ------------------------------------------
        # ADMIN
        # ------------------------------------------

        elif user and user.role == "ADMIN":

            # Administrator has full access.
            pass