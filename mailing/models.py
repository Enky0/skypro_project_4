from django.db import models
from django.utils import timezone
from users.models import BaseUser


# Create your models here.

class Message(models.Model):
    subject = models.CharField(max_length=50, verbose_name='Тема')
    body = models.TextField(verbose_name='Текст')
    owner = models.ForeignKey(BaseUser,
                              verbose_name='Владелец',
                              on_delete=models.CASCADE,
                              null=True,
                              blank=True)

    def __str__(self):
        return (f'Тема сообщения: {self.subject}\n'
                f'Сообщение: {self.body}')

    class Meta:
        verbose_name = 'сообщение'
        verbose_name_plural = 'сообщения'


class Recipient(models.Model):
    email = models.EmailField(unique=True, verbose_name='Email')
    initials = models.CharField(max_length=75, verbose_name='ФИО')
    commentary = models.TextField(blank=True, null=True, verbose_name='Комментарий')
    owner = models.ForeignKey(BaseUser,
                              verbose_name='Владелец',
                              on_delete=models.CASCADE,
                              null=True,
                              blank=True)

    def __str__(self):
        return (f'Email: {self.email}\n'
                f'ФИО: {self.initials}\n'
                f'Комментарий: {self.commentary}')

    class Meta:
        verbose_name = 'получатель рассылки'
        verbose_name_plural = 'получатели рассылки'
        permissions = [
            ('can_view_all_recipients', 'Возможность просматривать всех получателей'),
        ]


class Mailing(models.Model):
    STATUS_CREATED = 'created'
    STATUS_STARTED = 'started'
    STATUS_COMPLETED = 'completed'
    STATUS_PAUSED = 'paused'

    STATUS_CHOICES = [
        (STATUS_CREATED, 'Создана'),
        (STATUS_STARTED, 'Запущена'),
        (STATUS_COMPLETED, 'Завершена'),
        (STATUS_PAUSED, 'Приостановлена'),
    ]

    start_time = models.DateTimeField(verbose_name='Дата и время первой отправки')
    end_time = models.DateTimeField(verbose_name='Дата и время окончания отправки')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CREATED,
                              verbose_name='Статус отправки')
    message = models.ForeignKey('Message', on_delete=models.CASCADE, verbose_name='Сообщение')
    recipients = models.ManyToManyField('Recipient', verbose_name='Получатели')
    owner = models.ForeignKey(BaseUser,
                              verbose_name='Владелец',
                              on_delete=models.CASCADE,
                              null=True,
                              blank=True)

    def __str__(self):
        return (f'Дата и время первой отправки: {self.start_time}\n'
                f'Дата и время окончания отправки: {self.end_time}\n'
                f'Статус отправки: {self.status}\n'
                f'Сообщение: {self.message}')

    def update_status(self):
        current_time = timezone.now()

        if self.status == self.STATUS_PAUSED:
            return
        if self.owner and self.owner.is_blocked:
            new_status = self.STATUS_PAUSED
        elif current_time <= self.start_time:
            new_status = self.STATUS_CREATED
        elif self.start_time <= current_time < self.end_time:
            new_status = self.STATUS_STARTED
        else:
            new_status = self.STATUS_COMPLETED

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=['status'])

    class Meta:
        verbose_name = 'рассылка'
        verbose_name_plural = 'рассылки'
        permissions = [
            ('can_stop_mailings', 'Возможность приостановить рассылку пользователя'),
            ('can_view_all_mailings', 'Возможность просматривать все рассылки'),
        ]


class MailingAttempt(models.Model):
    STATUS_SUCCESS = 'success'
    STATUS_FAIL = 'fail'

    STATUS_CHOICES = [
        (STATUS_SUCCESS, 'Успешно'),
        (STATUS_FAIL, 'Не успешно'),
    ]

    attempt_date = models.DateTimeField(verbose_name='Дата и время попытки')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name='Статус попытки отправки')
    server_response = models.TextField(blank=True, verbose_name='Ответ почтового сервера')
    mailing = models.ForeignKey('Mailing', on_delete=models.CASCADE, verbose_name='Рассылка')

    def __str__(self):
        return (f'Дата и время попытки: {self.attempt_date}\n'
                f'Статус попытки отправки: {self.status}\n'
                f'Ответ почтового сервера: {self.server_response}')

    class Meta:
        verbose_name = 'попытка рассылки'
        verbose_name_plural = 'попытки рассылки'
