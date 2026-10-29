from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)

from accounts.access_control import (
    SupervisorRequiredMixin,
    TechnicianRequiredMixin,
)

from .forms import AssetCategoryForm, AssetForm
from .models import AssetCategory, Asset


# ==========================================
# ASSET CATEGORY VIEWS
# ==========================================


class AssetCategoryListView(TechnicianRequiredMixin, ListView):

    model = AssetCategory
    template_name = "assets/list.html"
    context_object_name = "categories"
    paginate_by = 10

    def get_queryset(self):

        search = self.request.GET.get("search")

        queryset = AssetCategory.objects.all()

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(description__icontains=search)
            )

        return queryset


class AssetCategoryCreateView(SupervisorRequiredMixin, CreateView):

    model = AssetCategory
    form_class = AssetCategoryForm
    template_name = "assets/form.html"
    success_url = reverse_lazy("assets:list")

    def form_valid(self, form):

        response = super().form_valid(form)

        messages.success(
            self.request,
            f'Asset category "{self.object.name}" was created successfully.'
        )

        return response


class AssetCategoryUpdateView(SupervisorRequiredMixin, UpdateView):

    model = AssetCategory
    form_class = AssetCategoryForm
    template_name = "assets/form.html"
    success_url = reverse_lazy("assets:list")

    def form_valid(self, form):

        response = super().form_valid(form)

        messages.success(
            self.request,
            f'Asset category "{self.object.name}" was updated successfully.'
        )

        return response


class AssetCategoryDeleteView(SupervisorRequiredMixin, DeleteView):

    model = AssetCategory
    template_name = "assets/confirm_delete.html"
    success_url = reverse_lazy("assets:list")

    def form_valid(self, form):

        category_name = self.object.name

        response = super().form_valid(form)

        messages.success(
            self.request,
            f'Asset category "{category_name}" was deleted successfully.'
        )

        return response


# ==========================================
# ASSET VIEWS
# ==========================================


class AssetListView(TechnicianRequiredMixin, ListView):

    model = Asset
    template_name = "assets/asset_list.html"
    context_object_name = "assets"
    paginate_by = 10

    def get_queryset(self):

        search = self.request.GET.get("search")

        queryset = Asset.objects.select_related(
            "category",
            "department"
        ).all()

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search)
                | Q(asset_tag__icontains=search)
                | Q(serial_number__icontains=search)
                | Q(location__icontains=search)
                | Q(category__name__icontains=search)
                | Q(department__name__icontains=search)
            )

        return queryset


class AssetCreateView(SupervisorRequiredMixin, CreateView):

    model = Asset
    form_class = AssetForm
    template_name = "assets/asset_form.html"
    success_url = reverse_lazy("assets:asset_list")

    def form_valid(self, form):

        response = super().form_valid(form)

        messages.success(
            self.request,
            f'Asset "{self.object.name}" was created successfully.'
        )

        return response


class AssetUpdateView(SupervisorRequiredMixin, UpdateView):

    model = Asset
    form_class = AssetForm
    template_name = "assets/asset_form.html"
    success_url = reverse_lazy("assets:asset_list")

    def form_valid(self, form):

        response = super().form_valid(form)

        messages.success(
            self.request,
            f'Asset "{self.object.name}" was updated successfully.'
        )

        return response


class AssetDeleteView(SupervisorRequiredMixin, DeleteView):

    model = Asset
    template_name = "assets/asset_confirm_delete.html"
    success_url = reverse_lazy("assets:asset_list")

    def form_valid(self, form):

        asset_name = self.object.name

        response = super().form_valid(form)

        messages.success(
            self.request,
            f'Asset "{asset_name}" was deleted successfully.'
        )

        return response