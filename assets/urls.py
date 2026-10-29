from django.urls import path
from . import views

app_name = "assets"

urlpatterns = [

    # =====================================
    # ASSET CATEGORY
    # =====================================

    path(
        "categories/",
        views.AssetCategoryListView.as_view(),
        name="list"
    ),

    path(
        "categories/add/",
        views.AssetCategoryCreateView.as_view(),
        name="add"
    ),

    path(
        "categories/<int:pk>/edit/",
        views.AssetCategoryUpdateView.as_view(),
        name="edit"
    ),

    path(
        "categories/<int:pk>/delete/",
        views.AssetCategoryDeleteView.as_view(),
        name="delete"
    ),


    # =====================================
    # ASSETS
    # =====================================

    path(
        "",
        views.AssetListView.as_view(),
        name="asset_list"
    ),

    path(
        "add/",
        views.AssetCreateView.as_view(),
        name="asset_add"
    ),

    path(
        "<int:pk>/edit/",
        views.AssetUpdateView.as_view(),
        name="asset_edit"
    ),

    path(
        "<int:pk>/delete/",
        views.AssetDeleteView.as_view(),
        name="asset_delete"
    ),
]