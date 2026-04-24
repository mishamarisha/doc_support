import requests as r
import hashlib
import sqlite3


url_prod = 'https://torgbox.ru/changelog.txt'
url_dev = 'https://dev.torgbox.ru/changelog.txt'


def create_tables():
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            hash TEXT PRIMARY KEY,
            date DATE,
            text TEXT,
            status NCHAR
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dev_tasks (
            hash TEXT PRIMARY KEY,
            date DATE,
            text TEXT,
            status NCHAR
        )
    ''')
    conn.commit()
    conn.close()


def get_file(url):
    if url == 'https://torgbox.ru/changelog.txt':
        response = r.get(url)
        response.raise_for_status()
        with open('changelog.txt', 'wb') as f:
            f.write(response.content)
    else:
        response = r.get(url)
        response.raise_for_status()
        with open('dev.changelog.txt', 'wb') as f:
            f.write(response.content)


def get_tasks(type):
    if type == 'prod':
        with open('changelog.txt', 'r', encoding='utf-8') as f:
            tasks = set(f.read().splitlines())
        return tasks
    elif type == 'dev':
        with open('dev.changelog.txt', 'r', encoding='utf-8') as f:
            tasks = set(f.read().splitlines())
        return tasks
    else:
        Exception('Получен неожиданный аргумент. Ожидаются: "prod", "dev"')


def get_hash_tasks(tasks):
    tasks_hash = {}
    for task in tasks:
        hash = hashlib.sha256(task.encode()).hexdigest()
        tasks_hash[hash] = task
    return tasks_hash


def add_tasks_prod(hash_hash, hash_tasks):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    for hash in hash_hash:
        text = hash_tasks[hash]
        date = text[0:10]
        text = text[11:]
        cursor.execute('''
                INSERT  OR IGNORE INTO tasks (hash, date, text, status)
                VALUES (?, ?, ?, ?)
            ''', (hash, date, text, 'new'))
    conn.commit()
    conn.close()


def add_tasks_dev(hash_hash, hash_tasks):
    conn = sqlite3.connect('my_database.db')
    cursor = conn.cursor()
    for hash in hash_hash:
        text = hash_tasks[hash]
        date = text[0:10]
        text = text[11:]
        cursor.execute('''
            INSERT  OR IGNORE INTO dev_tasks (hash, date, text, status)
            VALUES (?, ?, ?, ?)
        ''', (hash, date, text, 'new'))
    conn.commit()
    conn.close()


def main():

    # Скачиваем файлы
    get_file(url_prod)
    get_file(url_dev)

    # Считываем таски из файлов
    prod_tasks = get_tasks('prod')
    dev_tasks = get_tasks('dev')

    # Создаём словарь с ключами из хешей
    prod_hash_tasks = get_hash_tasks(prod_tasks)
    dev_hash_tasks = get_hash_tasks(dev_tasks)

    # Преобразуем ключи словаря во множество
    prod_hash = set(prod_hash_tasks.keys())
    dev_hash = set(dev_hash_tasks.keys())

    # Добавляем таски в БД
    add_tasks_prod(prod_hash, prod_hash_tasks)
    add_tasks_dev(dev_hash, dev_hash_tasks)


if __name__ == '__main__':
    main()
