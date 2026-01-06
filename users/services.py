from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import permission_required
from django.core.cache import cache
from users.models import BaseUser
from mailing.models import Mailing
from django.contrib import messages


@permission_required('users.can_block_users')
def block_user(request, user_id):
    """
    Функция для блокировки пользователя
    """
    user = get_object_or_404(BaseUser, id=user_id)

    if user == request.user:
        messages.error(request, 'Нельзя заблокировать себя')
        return redirect('user_list')

    if user.is_blocked:
        messages.error(request, 'Пользователь уже заблокирован')
        return redirect('user_list')

    user.is_blocked = True

    user.save()

    Mailing.objects.filter(owner=user, status='created').update(status='paused')
    Mailing.objects.filter(owner=user, status='started').update(status='paused')

    cache.delete('all_users_list')

    messages.success(
        request,
        f'Пользователь {user.email} заблокирован. '
        f'Рассылки приостановлены.'
    )

    return redirect('user_list')


@permission_required('users.can_block_users')
def unblock_user(request, user_id):
    """
    Функция для разблокировки пользователя
    """
    user = get_object_or_404(BaseUser, id=user_id)

    if user == request.user:
        messages.error(request, 'Нельзя заблокировать себя')
        return redirect('user_list')

    if not user.is_blocked:
        messages.error(request, 'Пользователь не заблокирован')
        return redirect('user_list')

    user.is_blocked = False

    user.save()

    cache.delete('all_users_list')

    messages.success(
        request,
        f'Пользователь {user.email} разблокирован. '
        f'Рассылки остаются приостановленными.'
    )

    return redirect('user_list')
