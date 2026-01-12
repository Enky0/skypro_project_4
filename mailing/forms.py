from django import forms
from django.utils import timezone
from mailing.models import Mailing, Recipient, Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'body']


class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ['email', 'initials', 'commentary']


class MailingForm(forms.ModelForm):
    start_time = forms.DateTimeField(
        input_formats=['%d.%m.%Y %H:%M:%S', '%d.%m.%Y %H:%M', '%d.%m.%Y'],
        widget=forms.DateTimeInput(
            format='%d.%m.%Y %H:%M:%S',
            attrs={'placeholder': '01.01.2026 00:00:00'}
        )
    )

    end_time = forms.DateTimeField(
        input_formats=['%d.%m.%Y %H:%M:%S', '%d.%m.%Y %H:%M', '%d.%m.%Y'],
        widget=forms.DateTimeInput(
            format='%d.%m.%Y %H:%M:%S',
            attrs={'placeholder': '01.01.2026 23:59:59'}
        )
    )

    def __init__(self, *args, **kwargs):
        # получение пользователя
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # фильтр сообщений и получателей только владельца рассылки
        if self.user:
            self.fields['message'].queryset = Message.objects.filter(owner=self.user)
            self.fields['recipients'].queryset = Recipient.objects.filter(owner=self.user)

    def clean_start_time(self):
        """
        Функция для валидации поля start_time
        :return:
        """
        start_time = self.cleaned_data.get('start_time')

        if not start_time:
            return start_time

        current_time = timezone.now()

        if start_time < current_time:
            raise forms.ValidationError('start_time не может быть в прошлом')

        return start_time

    def clean(self):
        cleaned_data = super().clean()

        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and start_time >= end_time:
            self.add_error('start_time', 'Необходимо выбрать время до времени окончания рассылки')
            self.add_error('end_time', 'Необходимо выбрать время после времени начала рассылки')

        return cleaned_data

    class Meta:
        model = Mailing
        fields = ['start_time', 'end_time', 'message', 'recipients']
