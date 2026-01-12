from django.core.management import BaseCommand
from mailing.models import Mailing
from mailing.services import attempt_mailing


class Command(BaseCommand):
    help = 'Отправить все рассылки со статусом created и started'

    def handle(self, *args, **options):
        mailings = Mailing.objects.filter(
            status__in=[Mailing.STATUS_CREATED, Mailing.STATUS_STARTED]
        )

        count = mailings.count()

        if count == 0:
            self.stdout.write('Нет рассылок для отправки')
            return

        for mailing in mailings:
            self.stdout.write(f'Отправляем рассылку #{mailing.id}')

            try:
                attempt_mailing(mailing)
                self.stdout.write(f'Рассылка #{mailing.id} отправлена')
            except Exception as e:
                self.stdout.write(f'Рассылка #{mailing.id} - Ошибка: {e}')

        self.stdout.write('Отправка рассылок завершена')
