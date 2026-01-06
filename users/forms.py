from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import BaseUser


class CustomSignupForm(UserCreationForm):
    phone = forms.CharField(
        max_length=11,
        required=False,
        label='Номер телефона',
        widget=forms.TextInput(attrs={'placeholder': '89012345678'})
    )

    country = forms.CharField(
        max_length=50,
        required=False,
        label='Страна',
        widget=forms.TextInput(attrs={'placeholder': 'Россия'})
    )

    avatar = forms.ImageField(
        required=False,
        label='Аватар',
        help_text='Загрузите своё фото'
    )

    class Meta:
        model = BaseUser
        fields = ('email', 'password1', 'password2', 'phone', 'country', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = 'Email'

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        if phone and not phone.isdigit():
            raise forms.ValidationError('Номер телефона должен содержать только цифры.')
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)

        user.phone = self.cleaned_data.get('phone', '')
        user.country = self.cleaned_data.get('country', '')

        if commit:
            user.save()
        return user
