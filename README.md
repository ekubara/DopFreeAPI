# dop-free-api

1. В корневой директории проекта создать виртуальное окружение

```sh
$ python3.10 -m venv venv
$ source venv/bin/activate
(venv) $ python -m pip install -r requirements.txt  
```

2. Создать базу данных

```sh
$ sudo -u postgres psql
postgres=# CREATE DATABASE название_базы_данных;
postgres=# CREATE USER имя_пользователя WITH PASSWORD 'пароль';
postgres=# ALTER ROLE имя_пользователя SET client_encoding TO 'utf8';
postgres=# ALTER ROLE имя_пользователя SET default_transaction_isolation TO 'read committed';
postgres=# ALTER ROLE имя_пользователя SET timezone TO 'Europe/London';
postgres=# GRANT ALL PRIVILEGES ON DATABASE название_базы_данных TO имя_пользователя;
postgres=# \q

```

3. Добавить данные в файл `.env`

```sh
HOST=127.0.0.1
PORT=8888

DB_USER=apiuser
DB_PASSWORD=apiuser
DB_HOST=localhost
DB_PORT=5432
DB_NAME=api
```
4. запуск
```sh
(venv) $ python migrations.py  
(venv) $ screen python main.py  
```