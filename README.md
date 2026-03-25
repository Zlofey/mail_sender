# mail_sender
тз для jetlend


# stack

- Django
- Celery + Redis
- SQLite
- Docker Compose

# запуск
```bash
# скопировать (заполнить) .env
cp .env.example .env

# запуск контейнеров
docker compose up --build

# Django management command.
docker compose exec web python manage.py import_mails <file.xlsx>