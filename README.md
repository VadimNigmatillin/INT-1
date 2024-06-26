# INT-1
Файл Create_table.py создает тестовую таблицу в базе данных.
![image](https://github.com/VadimNigmatillin/INT-1/assets/82418383/55d2fe74-cb0c-4ea5-9d35-937d14dea3c3)

Tests.py - файл для функционального и перфоманс тестирования.
В файле определены следующие основные элементы:  
-Установка параметров подключения к базе данных.  
-Создание объекта логгера для записи результатов тестов в файл.  
-Определение фикстуры для установки и закрытия соединения с базой данных.  
-Определение функций для логирования результатов поиска и создания индекса, если он не существует.  
-Функция "test_select_like" для функцианального тестирования.  
-Функция "test_performance_select_like" для перфоманс тестирования.  
-Обе функции используют параметризацию для выполнения тестов на различных наборах данных.

# Результат работы  
Тестовые данные для функционального тестирования  
![image](https://github.com/VadimNigmatillin/INT-1/assets/82418383/8a9aa5a7-79cb-44cb-af87-403336588b3a)  
Тестовые данные для перфоманс тестирования  
![image](https://github.com/VadimNigmatillin/INT-1/assets/82418383/4e17061d-367d-4694-b28e-fbb8bd1a522d)  
Результат работы  
![image](https://github.com/VadimNigmatillin/INT-1/assets/82418383/3ca63836-630f-4484-a8f6-d8aa3dd45e10)  
В файле test_mysql_select.log можно ознакомиться с результатами тестирования более подробно.  

Рассмотрим случай, когда индекс не будет использоваться.  
Индекс не будет работать, если символ % используется в начале шаблона, потому что индекс используется для ускорения поиска значений, начинающихся с указанного шаблона. Когда символ % расположен в начале шаблона, запрос требует полного перебора всех строк таблицы, чтобы найти соответствующие записи, что делает использование индекса непрактичным. Ниже прдеставлен запрос, который не будет использовать индекс.  
![image](https://github.com/VadimNigmatillin/INT-1/assets/82418383/7bd9b0d8-0a29-4bd8-b1e7-586bc79c342b)  
На скрине ниже видно, что все перфоманс тесты провалены.  
![image](https://github.com/VadimNigmatillin/INT-1/assets/82418383/e7d86ba7-2c96-4b32-a416-9423211a3f70)  
