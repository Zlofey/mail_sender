"""Команда для импорта рассылок из XLSX файла."""

from django.core.management.base import BaseCommand

from app.services.xlsx_importer import XLSXImporter


class Command(BaseCommand):
    """Команда для импорта рассылок из XLSX файла."""

    def add_arguments(self, parser) -> None:
        """Добавляет путь к файлу как аргумент команды."""
        parser.add_argument("file_path", type=str, help="Путь к файлу рассылок")

    def handle(self, *args, **options) -> None:
        """Основная логика команды."""
        file_path = options["file_path"]

        self.stdout.write(f"Starting import from {file_path}...")

        try:
            # запуск сервиса импорта
            importer = XLSXImporter(file_path)
            importer.run()

            # вывод статистики
            self._print_result(importer)

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Import failed: {str(e)}"))

    def _print_result(self, importer: XLSXImporter) -> None:
        """Выводит статистику импорта в консоль."""
        self.stdout.write(self.style.SUCCESS("=" * 50))
        self.stdout.write(self.style.SUCCESS("Import completed!"))
        self.stdout.write(self.style.SUCCESS(f"Processed rows: {importer.processed}"))
        self.stdout.write(self.style.SUCCESS(f"Created: {importer.created}"))
        self.stdout.write(
            self.style.WARNING(f"Skipped (duplicates): {importer.skipped}")
        )
        self.stdout.write(self.style.ERROR(f"Errors: {importer.errors}"))
        self.stdout.write(self.style.SUCCESS("=" * 50))
