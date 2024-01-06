from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import reverse, redirect
from django.views.generic.edit import FormView
from django.views import generic
from django.http import QueryDict, JsonResponse
from django.views import View

from .forms import OrderCreateForm
from .models import Note, Order, Client
from .mixins import ProfileCompletionRequiredMixin


class OrderListView(
    LoginRequiredMixin, ProfileCompletionRequiredMixin, generic.ListView
):
    template_name = "order_tracking/order_list.html"
    context_object_name = "order_list"

    def get_queryset(self):
        user = self.request.user
        queryset = (
            Order.objects.filter(company=user.company)
            .filter(deleted_flag=False)
            .filter(client__company=user.company)
        )
        return queryset


class OrderCreateView(LoginRequiredMixin, ProfileCompletionRequiredMixin, FormView):
    template_name = "order_tracking/order_create.html"
    context_object_name = "order_create"
    form_class = OrderCreateForm
    form = OrderCreateForm()
    success_url = "order_tracking:order_list"

    def form_valid(self, form):
        client_already_exists = self.request.POST.get('client_already_exists')

        if form.is_valid():
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
                    email=form.cleaned_data["email"]
                )
                client.save()

                order.client = client
                order.save()

            content = form.cleaned_data["content"]
            if content:
                note = Note.objects.create(
                    user=user,
                    order=order,
                    content=content
                )
                note.save()

            return redirect(self.get_success_url())

        else:
            return self.form_invalid(form)


class OrderUpdateView(LoginRequiredMixin, ProfileCompletionRequiredMixin, FormView):
    model = Order
    template_name = "order_tracking/order_update.html"
    form_class = OrderCreateForm
    context_object_name = "order_update"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Filter notes associated with the order, excluding deleted notes
        context["notes"] = Note.objects.filter(self.object, deleted_flag=False)
        return context

    def get_success_url(self):
        return reverse("order_tracking:order_list")

    def get_form_kwargs(self):
        kwargs = super(OrderUpdateView, self).get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(company=user.company)

    def form_valid(self, form):
        user = self.request.user
        order = form.save(commit=False)
        order_photo = self.request.FILES.get("order_photo")

        if order_photo and order_photo.size > (6 * 1024 * 1024):  # 6 MB
            form.add_error("order_photo", "File size should not exceed 6 MB.")
            return self.form_invalid(form)

        order.save()

        # Check for a new note in the request POST data
        note_content = self.request.POST.get("note_content")
        note_action = self.request.META.get("HTTP_X_NOTE_ACTION")

        if note_content and note_action == "create":
            # Create a new note and associate it with the current order
            note = Note.objects.create(order=order, content=note_content)
            note.company = user.company
            note.user = user
            note.order = order
            note.save()

        return super().form_valid(form)


class OrderDeleteView(LoginRequiredMixin, ProfileCompletionRequiredMixin, FormView):
    template_name = "order_tracking/order_delete.html"
    context_object_name = "order_delete"

    def get_success_url(self):
        return reverse("order_tracking:order_list")

    def get_queryset(self):
        user = self.request.user
        queryset = Order.objects.filter(company=user.company)
        queryset = queryset.filter(client__company=user.company)
        return queryset


class NoteUpdateView(LoginRequiredMixin, View):
    @staticmethod
    def post(request, pk):
        note_content = request.POST.get("note_content")
        if note_content:
            # Create a new note and associate it with the order (pk)
            note = Note.objects.create(
                order_id=pk,
                content=note_content,
                user=request.user,
                company=request.user.company,
            )
            return JsonResponse(
                {"success": True, "note_id": note.id, "timestamp": note.timestamp}
            )
        else:
            return JsonResponse({"success": False, "error": "Invalid note content."})


class NoteDeleteView(LoginRequiredMixin, ProfileCompletionRequiredMixin, FormView):
    @staticmethod
    def post(request, *args, **kwargs):
        try:
            note_id = request.POST.get("note_id")
            print("Received note ID:", note_id)
            note = Note.objects.get(pk=note_id)
            if note_id is not None:
                int(note_id)

                # Soft delete the note by setting the `deleted_flag` to True
                note.deleted_flag = True
                note.save()

                return JsonResponse({"success": True})
            else:
                return JsonResponse(
                    {"success": False, "error": "Note ID is missing or not valid"}
                )
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
