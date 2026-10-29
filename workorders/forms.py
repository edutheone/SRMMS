from django import forms
from .models import WorkOrder


class WorkOrderForm(forms.ModelForm):

    class Meta:
        model = WorkOrder

        fields = [
            "work_order_number",
            "title",
            "description",
            "service_request",
            "asset",
            "department",
            "assigned_to",
            "location",
            "priority",
            "status",
            "work_description",
            "completion_notes",
            "scheduled_date",
            "completed_date",
        ]

        widgets = {

            "work_order_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter work order number",
                }
            ),

            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter work order title",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe the work that needs to be done...",
                }
            ),

            "service_request": forms.Select(
                attrs={
                    "class": "form-select",
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

            "assigned_to": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter work location",
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

            "work_description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Describe the work performed...",
                }
            ),

            "completion_notes": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Enter final completion notes...",
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
        }

    def __init__(self, *args, **kwargs):

        user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)

        # -------------------------------------------------
        # TECHNICIAN PERMISSIONS
        # -------------------------------------------------

        if user and user.role == "TECHNICIAN":

            technician_fields = [
                "status",
                "work_description",
                "completion_notes",
                "completed_date",
            ]

            # Technician can only work on the fields
            # relevant to completing the Work Order.
            for field_name in self.fields:

                if field_name not in technician_fields:
                    self.fields[field_name].disabled = True

        # -------------------------------------------------
        # EMPLOYEE
        # -------------------------------------------------

        elif user and user.role == "EMPLOYEE":

            # Employees should not access Work Orders.
            self.fields.clear()

        # -------------------------------------------------
        # SUPERVISOR / ADMIN
        # -------------------------------------------------

        elif user and user.role in ["SUPERVISOR", "ADMIN"]:

            # These values come from the selected Service Request.
            # They will be populated by the view and must not
            # be manually changed by the Supervisor/Admin.
            request_fields = [
                "title",
                "description",
                "service_request",
                "asset",
                "department",
                "location",
                "priority",
                "status",
            ]

            for field_name in request_fields:
                self.fields[field_name].disabled = True

            # Work Order number remains available.
            # assigned_to remains available because the
            # Supervisor/Admin chooses the technician.
            #
            # Work-specific fields remain available for now:
            # work_description
            # completion_notes
            # scheduled_date
            # completed_date