# Трекер поддержки документации


# Импорт источников (очистка не выполняется)
python manage.py import_changelog

# Импорт только prod с очисткой старых записей
python manage.py import_changelog --source prod --clear

# Импорт только dev
python manage.py import_changelog --source dev

# Справка
python manage.py import_changelog --help
