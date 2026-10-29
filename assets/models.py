from django.db import models


class AssetCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Asset Category"
        verbose_name_plural = "Asset Categories"

    def __str__(self):
        return self.name


class Asset(models.Model):

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("maintenance", "Under Maintenance"),
        ("disposed", "Disposed"),
    ]

    name = models.CharField(
        max_length=150
    )

    asset_tag = models.CharField(
        max_length=50,
        unique=True
    )

    serial_number = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    category = models.ForeignKey(
        AssetCategory,
        on_delete=models.PROTECT,
        related_name="assets"
    )

    department = models.ForeignKey(
        "departments.Department",
        on_delete=models.PROTECT,
        related_name="assets"
    )

    location = models.CharField(
        max_length=150
    )

    purchase_date = models.DateField(
        null=True,
        blank=True
    )

    warranty_expiry = models.DateField(
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active"
    )

    description = models.TextField(
        blank=True
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
        return f"{self.asset_tag} - {self.name}"