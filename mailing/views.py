from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView, TemplateView, View
from .models import Recipient, Message, Mailing, MailingAttempt
from mailing.forms import MessageForm, RecipientForm, MailingForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .services import get_cached_queryset, attempt_mailing, pause_mailing, unpause_mailing
from django.shortcuts import get_object_or_404, redirect
from .mixins import BlockedUserMixin


# Create your views here.

# Модель Message

class MessageCreateView(BlockedUserMixin, LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        # Установка текущего пользователя как владельца
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = 'mailing/message_detail.html'
    context_object_name = 'message'

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailing/message_list.html'
    context_object_name = 'message_list'

    def get_queryset(self):
        cache_key = f'message_list_{self.request.user.id}'
        queryset = Message.objects.filter(owner=self.request.user)

        return get_cached_queryset(cache_key, queryset)


class MessageUpdateView(BlockedUserMixin, LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/message_form.html'

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse_lazy('message_detail', kwargs={'pk': self.object.pk})


class MessageDeleteView(BlockedUserMixin, LoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'mailing/message_confirm_delete.html'
    success_url = reverse_lazy('home')

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


# Модель Recipient

class RecipientCreateView(BlockedUserMixin, LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/recipient_form.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        # Установка текущего пользователя как владельца
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientDetailView(LoginRequiredMixin, DetailView):
    model = Recipient
    template_name = 'mailing/recipient_detail.html'
    context_object_name = 'recipient'

    def get_queryset(self):
        if self.request.user.has_perm('mailing.can_view_all_recipients'):
            return Recipient.objects.all()
        else:
            return Recipient.objects.filter(owner=self.request.user)


class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    template_name = 'mailing/recipient_list.html'
    context_object_name = 'recipients'

    def get_queryset(self):
        if self.request.user.has_perm('mailing.can_view_all_recipients'):
            cache_key = 'all_recipients_list'
            queryset = Recipient.objects.all()

            return get_cached_queryset(cache_key, queryset)

        cache_key = f'recipients_list_{self.request.user.id}'
        queryset = Recipient.objects.filter(owner=self.request.user)

        return get_cached_queryset(cache_key, queryset)


class RecipientUpdateView(BlockedUserMixin, LoginRequiredMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing/recipient_form.html'

    def get_queryset(self):
        return Recipient.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse_lazy('recipient_detail', kwargs={'pk': self.object.pk})


class RecipientDeleteView(BlockedUserMixin, LoginRequiredMixin, DeleteView):
    model = Recipient
    template_name = 'mailing/recipient_confirm_delete.html'
    success_url = reverse_lazy('home')

    def get_queryset(self):
        return Recipient.objects.filter(owner=self.request.user)


# Модель Mailing

class MailingCreateView(BlockedUserMixin, LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        # Передача пользователя в форму до валидации
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'
    context_object_name = 'mailing'

    def get_queryset(self):
        if self.request.user.has_perm('mailing.can_view_all_mailings'):
            return Mailing.objects.all()
        else:
            return Mailing.objects.filter(owner=self.request.user)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        if self.request.user.has_perm('mailing.can_view_all_mailings'):
            cache_key = 'all_mailings_list'
            queryset = Mailing.objects.all()

            return get_cached_queryset(cache_key, queryset)

        cache_key = f'mailings_list_{self.request.user.id}'
        queryset = Mailing.objects.filter(owner=self.request.user)

        return get_cached_queryset(cache_key, queryset)


class MailingUpdateView(BlockedUserMixin, LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/mailing_form.html'

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse_lazy('mailing_detail', kwargs={'pk': self.object.pk})


class MailingDeleteView(BlockedUserMixin, LoginRequiredMixin, DeleteView):
    model = Mailing
    template_name = 'mailing/mailing_confirm_delete.html'
    success_url = reverse_lazy('home')

    def get_queryset(self):
        return Mailing.objects.filter(owner=self.request.user)


class StatisticsView(LoginRequiredMixin, TemplateView):
    template_name = 'mailing/statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        successful_attempts = MailingAttempt.objects.filter(
            mailing__owner=user,
            status='success'
        ).count()

        failed_attempts = MailingAttempt.objects.filter(
            mailing__owner=user,
            status='fail'
        ).count()

        total_mailing_attempts = successful_attempts + failed_attempts

        context['total_successful_attempts'] = successful_attempts
        context['total_failed_attempts'] = failed_attempts
        context['total_mailing_attempts'] = total_mailing_attempts

        return context


class MailingAttemptListView(LoginRequiredMixin, ListView):
    model = MailingAttempt
    template_name = 'mailing/mailing_attempt_list.html'
    context_object_name = 'attempts'

    def get_queryset(self):
        queryset = MailingAttempt.objects.filter(mailing__owner=self.request.user).select_related('mailing',
                                                                                                  'mailing__message')

        cache_key = f'mailing_attempt_list_{self.request.user.id}'
        return get_cached_queryset(cache_key, queryset)


class HomePageView(TemplateView):
    template_name = 'mailing/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['total_mailings'] = Mailing.objects.count()
        context['active_mailings'] = Mailing.objects.filter(status=Mailing.STATUS_STARTED).count()
        context['unique_recipients'] = Recipient.objects.count()

        return context


class SendMailingView(BlockedUserMixin, LoginRequiredMixin, View):
    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)

        attempt_mailing(mailing)

        return redirect('mailing_detail', pk=pk)


class PauseMailingView(BlockedUserMixin, LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'mailing.can_stop_mailings'

    def post(self, request, pk):
        return pause_mailing(request, pk)


class UnpauseMailingView(BlockedUserMixin, LoginRequiredMixin, View):
    def post(self, request, pk):
        return unpause_mailing(request, pk)
