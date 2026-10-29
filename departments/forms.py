from django import forms
from .models import Department


class DepartmentForm(forms.ModelForm):

    class Meta:
        model = Department

        fields = [
            "code",
            "name",
            "description",
            "location",
            "email",
            "phone",
            "is_active",
        ]

        widgets = {
            "code": forms.TextInput(attrs={"class":"form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "location": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }