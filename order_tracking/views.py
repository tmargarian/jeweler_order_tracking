from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import reverse, redirect
from django.views.generic.edit import FormView
from .forms import OrderCreateForm, ClientCreateForm
from .models import Client, Note, Order
from django.views import generic
from django.http import QueryDict, JsonResponse
from django.views import View


class OrderListView(LoginRequiredMixin, generic.ListView):
    template_name = "order_tracking/order_list.html"
    context_object_name = "order_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Order status setup
        context['all_possible_statuses'] = ['Completed', 'Cancelled', 'In Progress']
        context['selected_statuses'] = self.request.GET.getlist('order_status')

        ordert_statuses_query_dict = QueryDict(mutable=True)
        ordert_statuses_query_dict.setlist('order_status', self.request.GET.getlist('order_status'))
        context['order_status_query_string'] = ordert_statuses_query_dict.urlencode()

    def get_queryset(self):
        user = self.request.user
        statuses = self.request.GET.getlist('order_status', None)
        client_ids = self.request.GET.getlist('client_id', None)
        sort_by = self.request.GET.get('sort_by', '-created_at')
        queryset = Order.objects \
            .filter(company=user.company) \
            .filter(deleted_flag=False) \
            .filter(client__company=user.company)

        if sort_by.replace('-', '') not in ['order_date', 'order_due_date']:
            sort_by = '-created_at'

            if statuses:
                queryset = queryset.filter(order_status__in=statuses)

            if client_ids:
                queryset = queryset.filter(client__id__in=client_ids)

            queryset = queryset.order_by(sort_by)
        else:
            return KeyError("User does not have permission to view orders")
        return queryset


class OrderCreateView(LoginRequiredMixin, FormView):
    template_name = "order_tracking/order_create.html"
    form_class = OrderCreateForm
    context_object_name = "order_create"

    def get_success_url(self):
        return reverse("order_tracking:order_list")

    def get(self, request, *args, **kwargs):
        client_form = ClientCreateForm()
        return self.render_to_response(self.get_context_data(client_form=client_form))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        client_already_exists = self.request.POST.get('client_already_exists')
        client_form = ClientCreateForm(self.request.POST)

        if form.is_valid() and client_form.is_valid():
            order = form.save(commit=False)
            order.company = self.request.user.company
            order.user = self.request.user
            order_photo = self.request.FILES.get('order_photo')
            if order_photo and order_photo.size > (6 * 1024 * 1024):  # 6 MB
                form.add_error('order_photo', "File size should not exceed 6 MB.")
                return self.form_invalid(form)

            if client_already_exists == 'True':
                if 'client' in form.cleaned_data and form.cleaned_data['client']:
                    order.client = form.cleaned_data['client']
                    order.save()
                else:
                    form.add_error('client', "Client must be selected when Client Already Exists is checked.")

            elif client_already_exists == 'False':
                if (client_form.cleaned_data.get('first_name') != ''
                        and client_form.cleaned_data.get('last_name') != ''
                        and client_form.cleaned_data.get('phone_number') != ''):
                    client = Client.objects.create(
                        company=self.request.user.company,
                        user=self.request.user,
                        order=order,
                        first_name=client_form.cleaned_data['first_name'],
                        last_name=client_form.cleaned_data['last_name'],
                        email=client_form.cleaned_data['email'],
                        phone_number=client_form.cleaned_data['phone_number'],
                    )
                    order.client = client
                    client.save()
                    order.save()

                else:
                    form.add_error('client', "Create a new client or check the box.")

            # Check for a new note in the request POST data
            note_content = self.request.POST.get('note_content')

            if note_content:
                # Create a new note and associate it with the current order
                note = Note.objects.create(order=order, content=note_content)
                note.company = self.request.user.company
                note.user = self.request.user
                note.order = order
                note.save()

            return redirect(self.get_success_url())
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['client_form'] = kwargs.get('client_form', ClientCreateForm())
        return context


class OrderUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Order
    template_name = "order_tracking/order_update.html"
    form_class = OrderCreateForm
    context_object_name = "order_update"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Filter notes associated with the order, excluding deleted notes
        context['notes'] = Note.objects.filter(order=self.object, deleted_flag=False)
        return context

    def get_success_url(self):
        return reverse("order_tracking:order_list")

    def get_form_kwargs(self):
        kwargs = super(OrderUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(company=user.company)

    def form_valid(self, form):
        user = self.request.user
        order = form.save(commit=False)
        order_photo = self.request.FILES.get('order_photo')

        if order_photo and order_photo.size > (6 * 1024 * 1024):  # 6 MB
            form.add_error('order_photo', "File size should not exceed 6 MB.")
            return self.form_invalid(form)

        order.save()

        # Check for a new note in the request POST data
        note_content = self.request.POST.get('note_content')
        note_action = self.request.META.get('HTTP_X_NOTE_ACTION')

        if note_content and note_action == 'create':
            # Create a new note and associate it with the current order
            note = Note.objects.create(order=order, content=note_content)
            note.company = user.company
            note.user = user
            note.order = order
            note.save()

        return super().form_valid(form)


class OrderDeleteView(LoginRequiredMixin, generic.DeleteView):
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
        note_content = request.POST.get('note_content')
        if note_content:
            # Create a new note and associate it with the order (pk)
            note = Note.objects.create(
                order_id=pk,
                content=note_content,
                user=request.user,
                company=request.user.company
            )
            return JsonResponse({'success': True, 'note_id': note.id, 'timestamp': note.timestamp})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid note content.'})


class NoteDeleteView(LoginRequiredMixin, View):
    @staticmethod
    def post(request, *args, **kwargs):
        try:
            note_id = request.POST.get('note_id')
            print("Received note ID:", note_id)
            note = Note.objects.get(pk=note_id)
            if note_id is not None:
                int(note_id)

                # Soft delete the note by setting the `deleted_flag` to True
                note.deleted_flag = True
                note.save()

                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Note ID is missing or not valid'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
