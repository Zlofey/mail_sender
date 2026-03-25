from django.db import models
from django.utils import timezone


class MailLog(models.Model):
    """Модель для хранения истории импорта рассылок."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("error", "Error"),
    ]

    external_id = models.CharField(max_length=255, unique=True, db_index=True)
    user_id = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField()
    subject = models.CharField(max_length=500)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Newsletter Log"
        verbose_name_plural = "Newsletter Logs"

    def __str__(self):
        return f"{self.external_id} - {self.email}"
