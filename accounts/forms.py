
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Username",
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Password",
        })
    )


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "phone_number",
            "role",
        )
        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "First name",
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Last name",
            }),
            "username": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Username",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Email address",
            }),
            "phone_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Phone number",
                "type": "tel",
            }),
            "role": forms.Select(attrs={
                "class": "form-select",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Administrators create supervisors, technicians and employees.
        self.fields["role"].choices = [
            (User.SUPERVISOR, "Supervisor"),
            (User.TECHNICIAN, "Technician"),
            (User.EMPLOYEE, "Employee"),
        ]

        self.fields["password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Enter password",
        })

        self.fields["password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Confirm password",
        })


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "phone_number",
            "role",
            "is_active",
        )
        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "First name",
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Last name",
            }),
            "username": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Username",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Email address",
            }),
            "phone_number": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Phone number",
                "type": "tel",
            }),
            "role": forms.Select(attrs={
                "class": "form-select",
            }),
            "is_active": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }
