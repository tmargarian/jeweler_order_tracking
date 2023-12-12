from django.urls import path

from .views import (
    OrderListView, OrderCreateView, OrderUpdateView, OrderDeleteView,
    NoteUpdateView, NoteDeleteView,
)

app_name = "order_tracking"

urlpatterns = [
    path("order_list/", OrderListView.as_view(), name="order_list"),
    path("order_create/", OrderCreateView.as_view(), name="order_create"),
    path("order_update/<uuid:pk>/", OrderUpdateView.as_view(), name="order_update"),
    path("order_delete/<uuid:pk>/", OrderDeleteView.as_view(), name="order_delete"),

    path("note_update/<pk>/", NoteUpdateView.as_view(), name="note_update"),
    path("note_delete/<pk>/", NoteDeleteView.as_view(), name="note_delete"),
]
