import pymysql
import random
from faker import Faker

# Устанавливаем параметры подключения
HOST = ''                       # Адрес хоста
USER = ''                       # Имя пользователя
PASSWORD = ''                   # Пароль для указанного пользователя
DATABASE = ''                   # Имя базы данных
table_name = 'USERS_TEST_TABLE' # Название таблицы
itog_count = 10000              # Количество записей
fake = Faker()

# Функция для генерации номера телефона только из цифр и длиной от 7 до 11
def generate_phone_number():
    length = random.randint(7, 11)
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

# Проверка существования таблицы
def table_exists(cursor, table_name):
    try:
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        return cursor.fetchone() is not None
    except pymysql.MySQLError as e:
        print(f"Ошибка при проверке существования таблицы: {e}")
        return False

def create_and_fill_table(cursor, table_name):
    
    # Создание таблицы
    create_table_query = f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        phone_number VARCHAR(15) UNIQUE,
        email VARCHAR(100) UNIQUE
    )
    '''
    try:
        cursor.execute(create_table_query)
        
        # Генерация и вставка данных
        insert_query = f'''
        INSERT INTO {table_name} (first_name, last_name, phone_number, email)
        VALUES (%s, %s, %s, %s)
        '''
        
        # Проверка количества записей в таблице
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        records_to_add = itog_count - count  # Определяем, сколько записей не хватает
        
        if records_to_add > 0:
            unique_phone_numbers = set()
            unique_emails = set()
            
            # Добавляем недостающие записи
            for _ in range(records_to_add):
                phone_number = generate_phone_number()
                email = fake.unique.email()
                
                # Генерация уникальных данных
                while phone_number in unique_phone_numbers:
                    phone_number = generate_phone_number()
                while email in unique_emails:
                    email = fake.unique.email()
                
                unique_phone_numbers.add(phone_number)
                unique_emails.add(email)
                
                cursor.execute(insert_query, (
                    fake.first_name(),
                    fake.last_name(),
                    phone_number,
                    email
                ))
            print(f"Таблица '{table_name}' успешно создана и заполнена данными.")
        else:
            print(f"Таблица '{table_name}' уже существует и содержит достаточное количество данных.")
    except pymysql.MySQLError as e:
        print(f"Ошибка при создании и заполнении таблицы '{table_name}': {e}")

try:
    # Устанавливаем соединение с базой данных
    with pymysql.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DATABASE
    ) as connection:
        with connection.cursor() as cursor:
            # Создаем или дополняем таблицу
            create_and_fill_table(cursor, table_name)
            # Подтверждаем изменения
            connection.commit()

except pymysql.MySQLError as e:
    print(f"Ошибка при работе с MySQL: {e}")
