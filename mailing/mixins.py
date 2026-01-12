from django.contrib import messages
from django.shortcuts import redirect


class BlockedUserMixin:
    """Миксин для запрета доступа заблокированным пользователям"""

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_blocked:
            messages.error(request, 'Ваш аккаунт заблокирован. Действие невозможно.')
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)
