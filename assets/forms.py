# assets/forms.py

from django import forms
from .models import AssetCategory, Asset


class AssetCategoryForm(forms.ModelForm):

    class Meta:
        model = AssetCategory

        fields = [
            "name",
            "description",
            "is_active",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter asset category name",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Enter category description",
                }
            ),

            "is_active": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }


class AssetForm(forms.ModelForm):

    class Meta:
        model = Asset

        fields = [
            "name",
            "asset_tag",
            "serial_number",
            "category",
            "department",
            "location",
            "purchase_date",
            "warranty_expiry",
            "status",
            "description",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter asset name",
                }
            ),

            "asset_tag": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. AST-0001",
                }
            ),

            "serial_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter serial number",
                }
            ),

            "category": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "department": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "location": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. ICT Office",
                }
            ),

            "purchase_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "warranty_expiry": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "status": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Enter asset description",
                }
            ),
        }