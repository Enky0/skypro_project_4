from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from mailing.models import MailingAttempt, Mailing
from config.settings import CACHE_ENABLED
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import permission_required


def send_email_to_recipient(recipient, message):
    """
    Функция для отправки письма получателю на электронную почту
    :param recipient: модель Recipient
    :param message: модель Message
    :return: status, server_response для создания объекта модели MailingAttempt
    """
    try:
        send_mail(
            subject=message.subject,
            message=message.body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient.email],
            fail_silently=False,
        )

        return MailingAttempt.STATUS_SUCCESS, 'Письмо успешно отправлено'

    except Exception as e:
        return MailingAttempt.STATUS_FAIL, f'Ошибка: {e}'


def get_mailing_recipients(mailing):
    """
    Функция получения всех получателей рассылки
    :param mailing: модель Mailing
    :return: QuerySet
    """
    return mailing.recipients.all()


def check_mailing_time(mailing):
    """
    Функция для проверки корректности даты рассылки
    :param mailing: модель Mailing
    :return: bool
    """
    current_time = timezone.now()
    start_time = mailing.start_time
    end_time = mailing.end_time

    # проверки корректны ли входящие данные
    if start_time is None:
        raise ValueError('start_time не должен быть None')
    if end_time is None:
        raise ValueError('end_time не должен быть None')

    if start_time <= current_time < end_time:
        return True
    else:
        return False


def check_mailing_status(mailing):
    """
    Функция для проверки актуальности статуса рассылки
    :param mailing: модель Mailing
    :return: bool
    """
    if mailing.status in [mailing.STATUS_COMPLETED, mailing.STATUS_PAUSED]:
        return False

    if mailing.status in [mailing.STATUS_STARTED, mailing.STATUS_CREATED]:
        return True


def attempt_mailing(mailing):
    """
    Функция для попытки рассылки писем получателям
    :param mailing: модель Mailing
    :return:
    """

    mailing.update_status()  # обновление статуса для проверки актуальности рассылки

    # проверка актуальности рассылки
    if not check_mailing_status(mailing):
        MailingAttempt.objects.create(
            mailing=mailing,
            attempt_date=timezone.now(),
            status=MailingAttempt.STATUS_FAIL,
            server_response='Рассылка уже завершена',
        )
        return

    # Проверка на неудачные сценарии функции check_mailing_time()
    try:
        if not check_mailing_time(mailing):
            MailingAttempt.objects.create(
                mailing=mailing,
                attempt_date=timezone.now(),
                status=MailingAttempt.STATUS_FAIL,
                server_response='Не подходящее время рассылки',
            )
            return

    except ValueError as e:
        MailingAttempt.objects.create(
            mailing=mailing,
            attempt_date=timezone.now(),
            status=MailingAttempt.STATUS_FAIL,
            server_response=f'Ошибка данных: {e}',
        )
        return

    # проверка что recipients существует
    recipients = get_mailing_recipients(mailing)
    if not recipients.exists():
        MailingAttempt.objects.create(
            mailing=mailing,
            attempt_date=timezone.now(),
            status=MailingAttempt.STATUS_FAIL,
            server_response='Список получателей пуст',
        )
        return

    # попытка рассылки
    for recipient in recipients:
        status, server_response = send_email_to_recipient(recipient, mailing.message)

        MailingAttempt.objects.create(
            mailing=mailing,
            attempt_date=timezone.now(),
            status=status,
            server_response=server_response,
        )

    mailing.update_status()


@permission_required('mailing.can_stop_mailings')
def pause_mailing(request, pk):
    """
    Функция для приостановки рассылки
    """

    mailing = get_object_or_404(Mailing, pk=pk)

    if mailing.status != mailing.STATUS_PAUSED:
        mailing.status = mailing.STATUS_PAUSED
        mailing.save(update_fields=['status'])
        messages.success(request, 'Рассылка приостановлена')
    else:
        messages.info(request, 'Рассылка уже приостановлена')

    return redirect('mailing_detail', pk=pk)


def unpause_mailing(request, pk):
    """
    Функция для возобновления приостановленной рассылки
    """

    mailing = get_object_or_404(Mailing, pk=pk, owner=request.user)

    if mailing.status != mailing.STATUS_PAUSED:
        messages.warning(request, 'Рассылка не приостановлена')
        return redirect('mailing_detail', pk=pk)

    # Проверка что пользователь не заблокирован
    if request.user.is_blocked:
        messages.error(request, 'Нельзя возобновить рассылку: ваш аккаунт заблокирован')
        return redirect('mailing_detail', pk=pk)

    mailing.status = mailing.STATUS_CREATED
    mailing.save(update_fields=['status'])

    mailing.update_status()

    messages.success(request, 'Рассылка возобновлена')
    return redirect('mailing_detail', pk=pk)


def get_cached_queryset(cache_key, queryset):
    """
    Функция для получения данных из кеша/кеширования
    """
    if not CACHE_ENABLED:
        return queryset

    cached_data = cache.get(cache_key)
    if cached_data is not None:
        return cached_data

    cache.set(cache_key, queryset, 60)
    return queryset
