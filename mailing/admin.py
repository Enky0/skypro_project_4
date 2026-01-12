from django.contrib import admin
from .models import Message, Recipient, Mailing, MailingAttempt


# Register your models here.

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'body', 'owner')
    list_filter = ('owner',)
    search_fields = ('subject', 'body')


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('email', 'initials', 'commentary', 'owner')
    list_filter = ('owner',)
    search_fields = ('email', 'initials', 'commentary')


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_time', 'end_time', 'status', 'message', 'owner')
    list_filter = ('status', 'owner', 'start_time')
    search_fields = ('message__subject',)
    filter_horizontal = ('recipients',)


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ('attempt_date', 'status', 'mailing', 'server_response')
    list_filter = ('status', 'attempt_date')
    search_fields = ('server_response', 'mailing__message__subject')
