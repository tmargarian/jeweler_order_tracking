from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import reverse, get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Sum, Case, When, DecimalField, F
from django.views.generic import ListView, UpdateView, DeleteView, CreateView
from django.http import JsonResponse
from django.template.loader import render_to_string

from .mixins import CompleteProfileAndActiveSubscriptionMixin
from .forms import OrderCreateForm, OrderUpdateForm, ClientUpdateForm
from .models import Note, Order, Client
from accounts.models import UserPreferences


class OrderListView(
    LoginRequiredMixin, CompleteProfileAndActiveSubscriptionMixin, ListView
):
    model = Order
    template_name = "order_tracking/order_list.html"
    context_object_name = "order_list"
    ordering = "-created_at"

    def get_ordering(self):
        default_order = super().get_ordering()
        order_attributes = self.request.GET.get("order_by")

        if order_attributes:
            return order_attributes.split(",")
        else:
            return default_order

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user_preferences, created = (UserPreferences.objects
                                     .get_or_create(user_id = self.request.user.id))
        context["pagination_options"] = UserPreferences.PAGINATION_OPTIONS
        context["user_pagination_setting"] = user_preferences.orders_per_page

        context["order_statuses"] = Order.ORDER_STATUS_CHOICES
        context["order_types"] = Order.ORDER_TYPE_CHOICES

        context["clients"] = Client.objects.filter(user_id=self.request.user.id)

        return context

    def get_paginate_by(self, queryset):
        """
        Pulling the paginate_by from the page (if changed by user) or using the
        UserPreferences setting (10 by default)
        """
        user_preferences, created = (UserPreferences.objects
                                     .get_or_create(user_id = self.request.user.id))
        paginate_by = int(self.request.GET.get("paginate_by", user_preferences.orders_per_page))

        # Update user preferences
        if user_preferences.orders_per_page != paginate_by:
            user_preferences.orders_per_page = paginate_by
            user_preferences.save()

        if paginate_by == -1:
            return None  # Disable pagination
        else:
            return paginate_by


    def get_queryset(self):
        queryset = (
            super()
                .get_queryset()  # this is needed for self.ordering and get_ordering() to work
                .filter(company=self.request.user.company)  # only orders of the user's company
                .filter(deleted_flag=False)  # accounting for soft-deleted orders
        )

        # Order Status filter handling
        order_statuses = self.request.GET.getlist("order_status", None)

        if order_statuses:
            queryset = queryset.filter(order_status__in=order_statuses)

        # Order Types filter handling
        order_types = self.request.GET.getlist("order_type", None)

        if order_types:
            queryset = queryset.filter(order_type__in=order_types)

        # Clients
        clients = self.request.GET.getlist("client", None)
        if clients:
            queryset = queryset.filter(client_id__in=clients)

        return queryset

    def get(self, request, *args, **kwargs):
        is_ajax = request.headers.get('X-Requested-With') == "XMLHttpRequest"
        if is_ajax:
            pass
        else:
            return super().get(request, *args, **kwargs)

class OrderCreateView(
    LoginRequiredMixin, CompleteProfileAndActiveSubscriptionMixin, CreateView
):
    template_name = "order_tracking/order_create.html"
    context_object_name = "order_create"
    form_class = OrderCreateForm
    success_url = reverse_lazy("order_tracking:order_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get(self, request, *args, **kwargs):
        # AJAX handling for Client info autocomplete
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

        if is_ajax:
            client_id = request.headers.get("clientId")
            client = Client.objects.get(id=client_id)
            return JsonResponse(
                {
                    "first_name": client.first_name,
                    "last_name": client.last_name,
                    "phone_number": str(client.phone_number),
                    "email": client.email,
                }
            )

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        client_already_exists = self.request.POST.get("client_already_exists")
        user = self.request.user
        order = form.save(commit=False)
        order.company = user.company
        order.user = user

        if client_already_exists == "True":
            order.client = form.cleaned_data["client"]
            order.save()

        if client_already_exists == "False":
            client = Client.objects.create(
                company=user.company,
                user=user,
                client_already_exists=form.cleaned_data["client_already_exists"],
                first_name=form.cleaned_data["first_name"],
                last_name=form.cleaned_data["last_name"],
                phone_number=form.cleaned_data["phone_number"],
                email=form.cleaned_data["email"],
            )
            client.save()

            order.client = client
            order.save()

        content = form.cleaned_data["content"]
        if content:
            note = Note.objects.create(user=user, order=order, content=content)
            note.save()

        return super().form_valid(form)

    def form_invalid(self, form):
        context = self.get_context_data()
        print(context["form"].data)
        print(context["form"].errors)
        return super().form_invalid(form)


class OrderUpdateView(
    LoginRequiredMixin, CompleteProfileAndActiveSubscriptionMixin, UpdateView
):
    model = Order
    template_name = "order_tracking/order_update.html"
    form_class = OrderUpdateForm
    context_object_name = "order_update"

    def get_success_url(self):
        return reverse_lazy("order_tracking:order_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Filter notes associated with the order
        context["notes"] = Note.objects.filter(order=self.object)
        return context

    def get_form_kwargs(self):
        kwargs = super(OrderUpdateView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        order = form.save(commit=False)
        order.save()
        return super().form_valid(form)


class OrderDeleteView(
    LoginRequiredMixin, CompleteProfileAndActiveSubscriptionMixin, DeleteView
):
    model = Order
    template_name = "order_tracking/order_delete.html"
    success_url = reverse_lazy("order_tracking:order_list")

    def delete(self, request, *args, **kwargs):
        try:
            order = self.get_object()

            # Soft delete associated notes
            Note.objects.filter(order=order).update(deleted_flag=True)

            # Soft delete the order
            order.deleted_flag = True
            order.save()

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


class NoteUpdateView(
    LoginRequiredMixin, CompleteProfileAndActiveSubscriptionMixin, UpdateView
):
    def post(self, request, pk):
        content = self.request.POST.get("content")
        note_action = self.request.META.get("HTTP_X_NOTE_ACTION")
        if content and note_action == "create":
            # Create a new note and associate it with the order (pk)
            note = Note.objects.create(
                user=request.user,
                order=Order.objects.get(pk=pk),
                content=content,
            )
            note.save()

            return JsonResponse(
                {
                    "success": True,
                    "note_id": note.id,
                    "content": note.content,
                    "timestamp": note.timestamp,
                }
            )
        else:
            return JsonResponse({"success": False, "error": "Invalid note content."})


class NoteDeleteView(
    LoginRequiredMixin, CompleteProfileAndActiveSubscriptionMixin, DeleteView
):
    def post(self, request, *args, **kwargs):
        try:
            # Use get_object_or_404 to get the Note object or return a 404 response if not found
            note = get_object_or_404(Note, pk=int(self.kwargs.get("pk")))

            # Delete the note
            note.delete()

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})


class ClientListView(
    LoginRequiredMixin, CompleteProfileAndActiveSubscriptionMixin, ListView
):
    model = Client
    template_name = "order_tracking/client_list.html"
    context_object_name = "client_list"

    def get_queryset(self):
        user = self.request.user
        queryset = Client.objects.filter(company=user.company).filter(
            deleted_flag=False
        )
        queryset = queryset.annotate(
            total_spent_column=Sum(
                Case(
                    When(
                        orders__order_status__in=["Completed"],
                        orders__deleted_flag=False,
                        then=F("orders__quoted_price"),
                    ),
                    default=0.00,
                    output_field=DecimalField(),
                )
            )
        )
        return queryset


class ClientUpdateView(
    LoginRequiredMixin, CompleteProfileAndActiveSubscriptionMixin, UpdateView
):
    model = Client
    template_name = "order_tracking/client_update.html"
    form_class = ClientUpdateForm
    context_object_name = "client_update"

    def get_success_url(self):
        return reverse("order_tracking:client_list")

    def get_form_kwargs(self):
        kwargs = super(ClientUpdateView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        client = form.save(commit=False)
        client.save()
        return super().form_valid(form)


class ClientDeleteView(
    LoginRequiredMixin, CompleteProfileAndActiveSubscriptionMixin, DeleteView
):
    model = Client
    template_name = "order_tracking/client_delete.html"
    success_url = reverse_lazy("order_tracking:client_list")

    def delete(self, request, *args, **kwargs):
        try:
            client = self.get_object()

            # Soft delete associated orders
            Order.objects.filter(client=client).update(deleted_flag=True)

            # Soft delete associated notes
            Note.objects.filter(client=client).update(deleted_flag=True)

            # Soft delete the client
            client.deleted_flag = True
            client.save()

            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
