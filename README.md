### Установка
+ склонировать репозиторий
```commandline
https://github.com/audiua/dev_XI
```

##### настройка переменных окружения
+ скопировать файл .env.example в .env
+ добавить свои настройки.   
Пример необходимых настроек:
```commandline
DEBUG=true
SECRET_KEY=0r^4chmbzsum32i(g-v$pc=7x942-22pde2^+))bv&pyo
STATIC_ROOT=/static
STATIC_URL=/static/
TIME_ZONE=Europe/Kiev
VOTING_PDF_DIR=voting_files
DATABASE=postgres
DB_NAME=postgres
DB_USER=postgres
DB_PASS=postgres
DB_SERVICE=postgres
DB_PORT=5432
```

##### запустить комманду в папке размещения файла docker-compose.yml
```commandline
docker-compose up
```
Если будут ошибки - permissions denied, запустить комманду в корне проекта
```commandline
sudo chown -R $USER:$USER .
```
И повторно запустить докер.

##### запускаем миграции
```commandline
docker-compose run --rm web python3 manage.py migrate
```
+ создаем админ юзера:
```commandline
docker-compose run --rm web python3 manage.py loaddata data.json
```
1. Создается admin:qwerty123 для доступа в [админ часть проекта](http://127.0.0.1:8000/admin/)  
PS. Этот шаг можно пропустить и создать юзера самому
```commandline
    docker-compose run --rm web python3 manage.py migrate createsuperuser
```

#### Добавления файлов pdf
+ файлы pdf([тут](https://drive.google.com/file/d/0B5_FQ3NcRoptYS1jX1pXcG4wcUE/view)) разместить в папку
/sources/<VOTING_PDF_DIR>. Если будут ошибки - permissions denied, запустить комманду в корне проекта
```commandline
sudo chown -R $USER:$USER .
``` 

###Ура :), окружение запущено!  
админка - [127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)  
api - [127.0.0.1:8000/api/v1/](http://127.0.0.1:8000/api/v1/)  
pgadmin4 - [127.0.0.1:5050](http://127.0.0.1:5050)  

### Логика приложения
Файлы pdf сначала конвертируются в html.  
Потом парсер получает нужные данные из html файлов и сохраняет в базу.

#### Конвертация pdf -> html:
+ для запуска конвертации 
```commandline
    docker-compose run --rm web python3 manage.py pdf2html
```
+ Комманда конвертации запускается по крону. Она сканирует 
папку sources/<VOTING_PDF_DIR> и все новые файлы конвертирует в html и разбивает на страницы

#### Парсинг html файлов
+ для запуска парсера
```commandline
    docker-compose run --rm web python3 manage.py parse_law
```

+ Комманда парсинга запускается по крону. Она парсит все новые файлы в 
папке sources/<VOTING_PDF_DIR>/


