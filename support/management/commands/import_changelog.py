import hashlib
import requests
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from support.models import ImportedChange


class Command(BaseCommand):
    help = 'Импортирует changelog.txt с prod и dev серверов в модель ImportedChange'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            choices=['prod', 'dev', 'both'],
            default='both',
            help='Какой источник импортировать: prod, dev или both (по умолч.)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить существующие записи для указанного источника перед импортом'
        )

    def handle(self, *args, **options):
        source = options['source']
        clear = options['clear']

        urls = {
            'prod': 'https://torgbox.ru/changelog.txt',
            'dev': 'https://dev.torgbox.ru/changelog.txt',
        }

        sources_to_process = ['prod', 'dev'] if source == 'both' else [source]

        for src in sources_to_process:
            self.stdout.write(f'Обработка источника: {src}')
            if clear:
                deleted, _ = ImportedChange.objects.filter(source=src).delete()
                self.stdout.write(f'  Удалено записей: {deleted}')

            url = urls[src]
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
            except requests.RequestException as e:
                raise CommandError(f'Ошибка загрузки {url}: {e}')

            lines = response.text.splitlines()
            self.stdout.write(f'  Загружено строк: {len(lines)}')

            created_count = 0
            skipped_count = 0

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Парсинг: ожидаем дату в начале строки в формате YYYY-MM-DD
                if len(line) < 10 or line[4] != '-' or line[7] != '-':
                    self.stdout.write(self.style.WARNING(f'    Пропущена строка (неверный формат даты): {line[:50]}'))
                    skipped_count += 1
                    continue

                date_str = line[:10]
                text = line[11:].strip()  # всё после даты и пробела
                if not text:
                    self.stdout.write(self.style.WARNING(f'    Пропущена строка (пустой текст): {line}'))
                    skipped_count += 1
                    continue

                # Преобразуем дату
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    self.stdout.write(self.style.WARNING(f'    Неверная дата: {date_str}'))
                    skipped_count += 1
                    continue

                # Вычисляем хеш (можно от полной строки)
                full_line = f"{date_str} {text}"
                hash_hex = hashlib.sha256(full_line.encode('utf-8')).hexdigest()

                try:
                    obj, created = ImportedChange.objects.get_or_create(
                        hash=hash_hex,
                        defaults={
                            'source': src,
                            'date': date_obj,
                            'text': text,
                        }
                    )
                    if created:
                        created_count += 1
                    else:
                        # запись уже существует
                        pass
                except IntegrityError:
                    self.stdout.write(self.style.ERROR(f'    Ошибка целостности для хеша: {hash_hex}'))
                    skipped_count += 1
                    continue

            self.stdout.write(self.style.SUCCESS(
                f'  Импорт завершён: +{created_count} новых, пропущено {skipped_count}'
            ))
