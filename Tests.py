import pytest
import pymysql
import time
import logging

# Устанавливаем параметры подключения
HOST = ''                  # Адрес хоста
USER = ''                  # Имя пользователя
PASSWORD = ''              # Пароль для указанного пользователя
DATABASE = ''              # Имя базы данных
TABLE_NAME = 'USERS_TEST_TABLE'  # Имя таблицы

# Имя файла логирования
log_filename = 'test_mysql_select.log'

# Создаем объект логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Создаем обработчик для записи в файл
file_handler = logging.FileHandler(log_filename)
file_handler.setLevel(logging.INFO)

# Создаем форматтер
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)

# Добавляем обработчик к логгеру
logger.addHandler(file_handler)

@pytest.fixture(scope='module')
def db_connection():
    """
    Фикстура для установки и закрытия соединения с базой данных.
    """
    connection = pymysql.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE
    )
    yield connection
    connection.close()

def log_results(func_name, pattern, result_count, query_time, indexed):
    """
    Логирование результатов поиска с использованием или без использования индекса.

    :param func_name: Имя функции
    :param pattern: Шаблон поиска
    :param result_count: Количество найденных записей
    :param query_time: Время выполнения запроса
    :param indexed: Был ли использован индекс
    """
    index_status = "с индексом" if indexed else "без индекса"
    logger.info(f"{func_name} - Результаты поиска (pattern: '{pattern}') {index_status}: {result_count} запись, время: {query_time:.6f} секунд")

def create_index_if_not_exists(cursor, table, column, index_name):
    """
    Создание индекса, если он не существует.

    :param cursor: Курсор базы данных
    :param table: Имя таблицы
    :param column: Имя колонки
    :param index_name: Имя индекса
    """
    cursor.execute(f"""
        SELECT COUNT(*)
        FROM INFORMATION_SCHEMA.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = '{table}'
        AND INDEX_NAME = '{index_name}'
    """)
    if cursor.fetchone()[0] == 0:
        cursor.execute(f"CREATE INDEX {index_name} ON {table} ({column})")
        cursor.connection.commit()

@pytest.mark.parametrize("column, pattern", [
    ("phone_number", "5143480"),
    ("phone_number", "3447899"),
    ("phone_number", "5172638"),
    ("email", "ylopez@example.com"),
    ("email", "kchung@example.org"),
    ("email", "david09@example.net")
])
def test_select_like(db_connection, column, pattern):
    """
    Тестирование запросов SELECT с использованием оператора LIKE без индекса и с индексом.

    :param db_connection: Соединение с базой данных
    :param column: Колонка для поиска
    :param pattern: Шаблон для поиска
    """
    index_name = f"idx_{column}_{pattern.replace('@', '_').replace('.', '_')}"
    with db_connection.cursor() as cursor:
        # Выполнение запроса без индекса
        start_time = time.time()
        cursor.execute(f"SELECT {column} FROM {TABLE_NAME} WHERE {column} LIKE '{pattern}'")
        result_without_index = cursor.fetchall()
        time_without_index = time.time() - start_time

        log_results(test_select_like.__name__, f"{column}: {pattern}", len(result_without_index), time_without_index, indexed=False)

        # Создание индекса
        create_index_if_not_exists(cursor, TABLE_NAME, column, index_name)

        # Выполнение запроса с индексом
        start_time = time.time()
        cursor.execute(f"SELECT {column} FROM {TABLE_NAME} WHERE {column} LIKE '{pattern}%'")
        result_with_index = cursor.fetchall()
        time_with_index = time.time() - start_time

        log_results(test_select_like.__name__, f"{column}: {pattern}", len(result_with_index), time_with_index, indexed=True)

        # Удаление индекса после теста
        cursor.execute(f"ALTER TABLE {TABLE_NAME} DROP INDEX {index_name}")
        db_connection.commit()

    # Проверка, что результаты запросов без индекса и с индексом совпадают
    assert result_without_index == result_with_index, "Результаты запросов без индекса и с индексом не совпадают"

    # Добавляем отступ между тестами
    logger.info("-"*50 + "\n")

@pytest.mark.parametrize("column, pattern", [
    ("phone_number", "8437772"),
    ("phone_number", "9159019"),
    ("phone_number", "5149780"),
    ("email", "ifloyd@example.com"),
    ("email", "rmora@example.org"),
    ("email", "lori23@example.com")
])
def test_performance_select_like(db_connection, column, pattern):
    """
    Проверка производительности запросов SELECT с использованием и без использования индекса.

    :param db_connection: Соединение с базой данных
    :param column: Колонка для поиска
    :param pattern: Шаблон для поиска
    """
    index_name = f"idx_{column}_{pattern.replace('@', '_').replace('.', '_')}"
    with db_connection.cursor() as cursor:
        # Замер времени выполнения запроса без индекса
        start_time_without_index = time.time()
        cursor.execute(f"EXPLAIN SELECT {column} FROM {TABLE_NAME} WHERE {column} LIKE '{pattern}'")
        result_without_index = cursor.fetchall()
        time_without_index = time.time() - start_time_without_index

        log_results(test_performance_select_like.__name__, f"{column}: {pattern}", len(result_without_index), time_without_index, indexed=False)

        # Создание индекса
        create_index_if_not_exists(cursor, TABLE_NAME, column, index_name)

        # Замер времени выполнения запроса с индексом
        start_time_with_index = time.time()
        cursor.execute(f"SELECT {column} FROM {TABLE_NAME} WHERE {column} LIKE '%{pattern}'")
        result_with_index = cursor.fetchall()
        time_with_index = time.time() - start_time_with_index

        log_results(test_performance_select_like.__name__, f"{column}: {pattern}", len(result_with_index), time_with_index, indexed=True)

        # Удаление индекса
        cursor.execute(f"ALTER TABLE {TABLE_NAME} DROP INDEX {index_name}")
        db_connection.commit()

    # Проверка производительности: запрос с индексом должен быть быстрее
    assert time_with_index < time_without_index, f"Запрос с индексом (время: {time_with_index:.6f} секунд) не работает быстрее запроса без индекса (время: {time_without_index:.6f} секунд)"

    # Добавляем отступ между тестами
    logger.info("-" * 50 + "\n")
