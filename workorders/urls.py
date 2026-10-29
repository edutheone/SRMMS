from django.urls import path
from . import views


app_name = "workorders"


urlpatterns = [

    # =====================================
    # WORK ORDERS
    # =====================================

    path(
        "",
        views.WorkOrderListView.as_view(),
        name="list"
    ),

    path(
        "add/",
        views.WorkOrderCreateView.as_view(),
        name="add"
    ),

    path(
        "<int:pk>/edit/",
        views.WorkOrderUpdateView.as_view(),
        name="edit"
    ),

    path(
        "<int:pk>/delete/",
        views.WorkOrderDeleteView.as_view(),
        name="delete"
    ),
]