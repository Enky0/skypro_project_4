from django.urls import path

from users.views import UserListView, UserDetailView, UserMailingsListView, UserRecipientsListView, BlockUserView, \
    UnblockUserView, CustomSignupView, UserUpdateView

urlpatterns = [
    path('signup/', CustomSignupView.as_view(), name='custom_signup'),
    path('users/', UserListView.as_view(), name='user_list'),
    path('users/<int:pk>', UserDetailView.as_view(), name='user_detail'),
    path('users/<int:pk>/edit/', UserUpdateView.as_view(), name='user_edit'),
    path('<int:pk>/mailings/', UserMailingsListView.as_view(), name='user_mailing_list'),
    path('<int:pk>/recipients/', UserRecipientsListView.as_view(), name='user_recipient_list'),
    path('<int:pk>/block_user/', BlockUserView.as_view(), name='block_user'),
    path('<int:pk>/unblock_user/', UnblockUserView.as_view(), name='unblock_user'),
]
