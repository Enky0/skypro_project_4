from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from mailing.services import get_cached_queryset
from mailing.models import Mailing, Recipient
from users.services import block_user, unblock_user
from django.contrib.auth import login
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .forms import CustomSignupForm
from .models import BaseUser
from django.contrib import messages


# Create your views here.

class CustomSignupView(CreateView):
    model = BaseUser
    form_class = CustomSignupForm
    template_name = 'users/signup.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save()

        login(self.request, user)

        messages.success(self.request, 'Регистрация прошла успешно!')

        return redirect(self.success_url)


class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = BaseUser
    template_name = 'users/user_list.html'
    context_object_name = 'user_list'
    permission_required = 'users.can_view_all_users'

    def get_queryset(self):
        cache_key = 'all_users_list'
        queryset = BaseUser.objects.all()
        return get_cached_queryset(cache_key, queryset)


class UserDetailView(LoginRequiredMixin, DetailView):
    model = BaseUser
    template_name = 'users/user_detail.html'
    context_object_name = 'user'


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = BaseUser
    fields = ['phone', 'country', 'avatar']
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('home')

    def get_object(self):
        return self.request.user


class UserMailingsListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'mailings'
    permission_required = 'users.can_view_all_users'

    def get_queryset(self):
        user_id = self.kwargs['pk']
        return Mailing.objects.filter(owner_id=user_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = BaseUser.objects.get(id=self.kwargs['pk'])
        return context


class UserRecipientsListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Recipient
    template_name = 'mailing/recipient_list.html'
    context_object_name = 'recipients'
    permission_required = 'users.can_view_all_users'

    def get_queryset(self):
        user_id = self.kwargs['pk']
        return Recipient.objects.filter(owner_id=user_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = BaseUser.objects.get(id=self.kwargs['pk'])
        return context


class BlockUserView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'users.can_block_users'

    def post(self, request, pk):
        return block_user(request, pk)


class UnblockUserView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'users.can_block_users'

    def post(self, request, pk):
        return unblock_user(request, pk)
