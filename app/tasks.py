import random
import time
import logging
from celery import shared_task
from django.utils import timezone

from app.models import MailLog

logger = logging.getLogger(__name__)


# max_retries - защита от бесконечных попыток
@shared_task(bind=True, max_retries=3)
def send_email_task(self, log_id: int) -> None:
    """
    Асинхронная задача отправки письма.

    Делаем задержку вместо отправки реального email.

    Args:
        log_id: ID записи MailLog для обновления статуса
    """
    try:
        # получаем запись из БД
        log_entry = MailLog.objects.get(id=log_id)

        # задержка
        delay = random.randint(5, 20)
        logger.info(f"Start sending to {log_entry.email}. Delay: {delay}s")
        time.sleep(delay)

        # логирование отправки
        logger.info(f"Send EMAIL to {log_entry.email}: {log_entry.subject}")
        print(f"Send EMAIL to {log_entry.email}: {log_entry.subject}")

        # обновляем статус
        log_entry.status = "sent"
        log_entry.processed_at = timezone.now()
        log_entry.save()

    except MailLog.DoesNotExist:
        # запись удалена или не создана — не делаем retry
        logger.error(f"MailLog with id {log_id} not found")
        return

    except Exception as exc:
        # любая другая ошибка — логируем и пробуем ещё раз
        logger.error(f"Failed to send email: {exc}")

        # обновляем статус на error, если объект есть
        if "log_entry" in locals():
            log_entry.status = "error"
            log_entry.save()

        # Retry с задержкой 60 секунд
        raise self.retry(exc=exc, countdown=60)
