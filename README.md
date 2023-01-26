# Курсовая работа

## Задачи

- [x] Прописать модель "Продукта"
- [ ] Прописать модель "Хранимого товара на складе и магазине"
- [ ] Взаимодействие со созданной моделью "Склада и магазина"
- [x] Реализовать базовый шаблон страницы
- [x] Отдельное приложенеи для user
- [x] Работа с EAV

## Дополнительные задачи

- [ ] Написать тесты
- [ ] Внедрить 'django-money' вместо Decimal

## Полезыне ссылки

- [JSONB в PostgreSQL](https://coussej.github.io/2016/01/14/Replacing-EAV-with-JSONB-in-PostgreSQL/)
- [Django интернет-магазин](https://pocoz.gitbooks.io/django-v-primerah/content/glava-7-sozdanie-internet-magazina.html)
- [Using Django for Inventory Management with FIFO](https://medium.com/@stevelukis/using-django-for-inventory-management-with-fifo-first-in-first-out-method-bbcac1b19f2c)
- [Выполнение сырых SQL-запросов](https://runebook.dev/ru/docs/django/topics/db/sql)
- [Интересные темы по django](https://www.cischool.ru/catalog/programming/python/programmirovanie-na-yazyke-python-razrabotka-veb-prilozhenij-v-django/)
- [Модели django](https://djangodoc.ru/3.2/topics/db/models/)
- [Что должно быть](https://github.com/SergeyLebidko/MiniStorage)
- [Модель для отображения JSON](https://ru.stackoverflow.com/questions/1222063/%D0%9A%D0%B0%D0%BA-%D0%B4%D0%BE%D0%B1%D0%B0%D0%B2%D0%BB%D1%8F%D1%82%D1%8C-%D1%85%D0%B0%D1%80%D0%B0%D0%BA%D1%82%D0%B5%D1%80%D0%B8%D1%81%D1%82%D0%B8%D0%BA%D0%B8-%D1%82%D0%BE%D0%B2%D0%B0%D1%80%D0%BE%D0%B2-%D1%87%D0%B5%D1%80%D0%B5%D0%B7-json-%D0%B4%D0%BB%D1%8F-%D0%BA%D0%B0%D0%B6%D0%B4%D0%BE%D0%B9-%D0%BA%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D0%B8)
- [InlineFormSet](https://docs.djangoproject.com/en/4.1/topics/forms/modelforms/#inline-formsets)
- [2 формы в одной](https://www.letscodemore.com/blog/django-inline-formset-factory-with-examples/)

## Интересные ссылки

- [django-money](https://github.com/django-money/django-money)


## Мысли и идеи

- В моделе приложения товааров используется EAV

## Подготовка БД для Django

В pgAdmin зайти на свой локальный сервер
После на нем создать новую базу данных

Создадим нового пользователя базы данных, который сможет использовать
для подключения и взаимодействия с БД

```sql
CREATE USER [имя пользователя] WITH PASSWORD 'тут пишим пароль к нему';
```

После нужно изменить несколько параметров подключения только что созданного
пользователя. Для ускорения операции с БД

```sql
ALTER ROLE [имя пользователя] SET client_encoding TO 'utf8';
```

```sql
ALTER ROLE [имя пользователя] SET default_transaction_isolation TO 'read committed';
```

```sql
ALTER ROLE [имя пользователя] SET timezone TO 'UTC';
```

Предоставляем пользователю БД права доступа к базе данных, которую создали

```sql
GRANT ALL PRIVILEGES ON DATABASE [название базы данных] TO [имя пользователя];
```

Заменить данные строчки DATABASES файла settings.py в папке ядра проекта

## Запуск сервера

Чтобы запустить сервер нужно находится в папке с файлом manage.py

```bash
python manage.py runserver
```

## Создание базы данных и просмотр sql-кода

Команда создания sql-запроса:

```bash
python manage.py makemigrations
```

Команда для просмотра созданного sql-запроса

```bash
python manage.py sqlmigrate [название приложения] [номер/название созданной миграции]
```

`Команда для выполнения миграции

```bash
python manage.py migrate
```

## Создание супер пользователя

Для входа в админ-панель нужно создать пользователя

```bash
python manage.py createsuperuser
```

## Работа с .env

Добавить env_template.txt в папку /core, заполнив данными и переименовав в .env