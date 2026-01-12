from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mailing.models import Recipient, Mailing
from users.models import BaseUser


class Command(BaseCommand):
    help = 'create manager group'

    def handle(self, *args, **options):
        try:
            # создание или получение группы
            group, created = Group.objects.get_or_create(name='Менеджер')

            # удаление лишних прав
            group.permissions.clear()

            mailing_content_type = ContentType.objects.get_for_model(Mailing)
            recipient_content_type = ContentType.objects.get_for_model(Recipient)

            # право видеть все рассылки
            try:
                can_view_mailings_perm = Permission.objects.get(
                    codename='can_view_all_mailings',
                    content_type=mailing_content_type,
                )
                group.permissions.add(can_view_mailings_perm)
                self.stdout.write('Добавлено: can_view_all_mailings')
            except Permission.DoesNotExist:
                self.stdout.write('Не найдено: can_view_all_mailings')

            # право видеть всех получателей
            try:
                can_view_recipients_perm = Permission.objects.get(
                    codename='can_view_all_recipients',
                    content_type=recipient_content_type,
                )
                group.permissions.add(can_view_recipients_perm)
                self.stdout.write('Добавлено: can_view_all_recipients')
            except Permission.DoesNotExist:
                self.stdout.write('Не найдено: can_view_all_recipients')

            # право на блокировку пользователя
            users_content_type = ContentType.objects.get_for_model(BaseUser)

            try:
                block_users_perm = Permission.objects.get(codename='can_block_users',
                                                          content_type=users_content_type)

                group.permissions.add(block_users_perm)

                self.stdout.write('Добавлено право: can_block_users')

            except Permission.DoesNotExist:
                self.stdout.write('Право can_block_users не найдено')

            # право на приостановку рассылки

            try:
                stop_mailings_perm = Permission.objects.get(codename='can_stop_mailings',
                                                            content_type=mailing_content_type)

                group.permissions.add(stop_mailings_perm)

                self.stdout.write('Добавлено право: can_stop_mailings')

            except Permission.DoesNotExist:
                self.stdout.write('Право can_stop_mailings не найдено')

            # право на просмотр всех пользователей
            try:
                view_user_perm = Permission.objects.get(
                    codename='can_view_all_users',
                    content_type=users_content_type
                )

                group.permissions.add(view_user_perm)

                self.stdout.write('Добавлено право: can_view_all_users')

            except Permission.DoesNotExist:
                self.stdout.write('Право can_view_all_users не найдено')

            if created:
                self.stdout.write(self.style.SUCCESS('Группа создана успешно'))
            else:
                self.stdout.write(self.style.WARNING('Группа уже существует'))

        except ObjectDoesNotExist as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: право {e} не найдено, проверьте выполнены ли миграции'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка: {e}'))
