from django.urls import path
from mailing.views import (
    HomePageView,
    StatisticsView,

    MessageListView, MessageDetailView,
    MessageCreateView, MessageUpdateView, MessageDeleteView,

    RecipientListView, RecipientDetailView,
    RecipientCreateView, RecipientUpdateView, RecipientDeleteView,

    MailingListView, MailingDetailView,
    MailingCreateView, MailingUpdateView, MailingDeleteView, SendMailingView, PauseMailingView, UnpauseMailingView,
    MailingAttemptListView,
)

urlpatterns = [
    path('home/', HomePageView.as_view(), name='home'),

    path('statistics/', StatisticsView.as_view(), name='statistics'),

    path('attempts/', MailingAttemptListView.as_view(), name='mailing_attempts'),

    path('messages/', MessageListView.as_view(), name='message_list'),
    path('messages/<int:pk>/', MessageDetailView.as_view(), name='message_detail'),
    path('messages/new/', MessageCreateView.as_view(), name='message_new'),
    path('messages/<int:pk>/edit/', MessageUpdateView.as_view(), name='message_edit'),
    path('messages/<int:pk>/delete/', MessageDeleteView.as_view(), name='message_delete'),

    path('recipients/', RecipientListView.as_view(), name='recipient_list'),
    path('recipients/<int:pk>/', RecipientDetailView.as_view(), name='recipient_detail'),
    path('recipients/new/', RecipientCreateView.as_view(), name='recipient_new'),
    path('recipients/<int:pk>/edit/', RecipientUpdateView.as_view(), name='recipient_edit'),
    path('recipients/<int:pk>/delete/', RecipientDeleteView.as_view(), name='recipient_delete'),

    path('mailings/', MailingListView.as_view(), name='mailing_list'),
    path('mailings/<int:pk>/', MailingDetailView.as_view(), name='mailing_detail'),
    path('mailings/new/', MailingCreateView.as_view(), name='mailing_new'),
    path('mailings/<int:pk>/edit/', MailingUpdateView.as_view(), name='mailing_edit'),
    path('mailings/<int:pk>/delete/', MailingDeleteView.as_view(), name='mailing_delete'),
    path('mailings/<int:pk>/send/', SendMailingView.as_view(), name='send_mailing'),
    path('mailings/<int:pk>/pause/', PauseMailingView.as_view(), name='pause_mailing'),
    path('mailings/<int:pk>/unpause/', UnpauseMailingView.as_view(), name='unpause_mailing'),
]
