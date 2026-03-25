import tempfile
import os
from django.test import TestCase
from openpyxl import Workbook

from app.models import MailLog
from app.services.xlsx_importer import XLSXImporter


class XLSXImporterTest(TestCase):
    """Тестирование бизнес-логики импорта."""

    def setUp(self):
        """Создаёт временный XLSX файл для тестов."""
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
        self.temp_file_path = self.temp_file.name
        self.temp_file.close()

    def tearDown(self):
        """Удаляет временный файл после теста."""
        if os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)

    def _create_test_file(self, rows):
        """
        Создаёт тестовый XLSX файл.

        Args:
            rows: Список строк (включая заголовки)
        """
        wb = Workbook()
        ws = wb.active

        for row in rows:
            ws.append(row)

        wb.save(self.temp_file_path)
        wb.close()

    def test_import_creates_records(self):
        """Проверяет, что импорт создаёт записи в БД."""
        # Arrange
        self._create_test_file(
            [
                ["external_id", "user_id", "email", "subject", "message"],
                ["001", "100", "test1@example.com", "Test 1", "Message 1"],
                ["002", "101", "test2@example.com", "Test 2", "Message 2"],
            ]
        )

        # Act
        importer = XLSXImporter(self.temp_file_path)
        importer.run()

        # Assert
        self.assertEqual(MailLog.objects.count(), 2)
        self.assertEqual(importer.created, 2)
        self.assertEqual(importer.processed, 2)
        self.assertEqual(importer.errors, 0)

    def test_import_skips_duplicates(self):
        """Проверяет идемпотентность — дубликаты не создаются."""
        # Arrange
        self._create_test_file(
            [
                ["external_id", "user_id", "email", "subject", "message"],
                ["001", "100", "test1@example.com", "Test 1", "Message 1"],
            ]
        )

        # Act — первый импорт
        importer1 = XLSXImporter(self.temp_file_path)
        importer1.run()

        # Act — повторный импорт
        importer2 = XLSXImporter(self.temp_file_path)
        importer2.run()

        # Assert
        self.assertEqual(MailLog.objects.count(), 1)  # Всё ещё 1 запись
        self.assertEqual(importer2.skipped, 1)  # Пропущен как дубликат
        self.assertEqual(importer2.created, 0)  # Ничего не создано

    def test_import_counts_errors(self):
        """Проверяет, что ошибки валидации считаются."""
        # Arrange — файл без обязательного поля email
        self._create_test_file(
            [
                ["external_id", "user_id", "email", "subject", "message"],
                ["001", "100", "", "Test 1", "Message 1"],  # пустой email
            ]
        )

        # Act
        importer = XLSXImporter(self.temp_file_path)
        importer.run()

        # Assert
        self.assertEqual(MailLog.objects.count(), 0)  # Запись не создана
        self.assertEqual(importer.errors, 1)  # 1 ошибка
        self.assertEqual(importer.processed, 1)  # 1 строка обработана

    def test_import_handles_missing_headers(self):
        """Проверяет, что импорт падает при отсутствии заголовков."""
        # Arrange — файл без обязательного заголовка
        self._create_test_file(
            [
                ["external_id", "user_id", "subject", "message"],  # нет email
                ["001", "100", "Test 1", "Message 1"],
            ]
        )

        # Act
        importer = XLSXImporter(self.temp_file_path)
        result = importer.run()

        # Assert
        self.assertEqual(MailLog.objects.count(), 0)
        self.assertEqual(result.created, 0)  # Ничего не создано


class MailLogTest(TestCase):
    """Тестирование модели MailLog."""

    def test_unique_external_id(self):
        """Проверяет уникальность external_id на уровне БД."""
        # Arrange
        MailLog.objects.create(
            external_id="001",
            email="test1@example.com",
            subject="Test",
            message="Message",
        )

        # Act & Assert — дубликат должен вызвать ошибку
        from django.db import IntegrityError

        with self.assertRaises(IntegrityError):
            MailLog.objects.create(
                external_id="001",  # тот же external_id
                email="test2@example.com",
                subject="Test 2",
                message="Message 2",
            )

    def test_status_choices(self):
        """Проверяет, что статусы записываются корректно."""
        # Arrange & Act
        log = MailLog.objects.create(
            external_id="001",
            email="test@example.com",
            subject="Test",
            message="Message",
            status="pending",
        )

        # Assert
        self.assertEqual(log.status, "pending")
        log.status = "sent"
        log.save()
        self.assertEqual(log.status, "sent")
