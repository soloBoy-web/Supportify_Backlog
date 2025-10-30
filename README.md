# Сервис по рассылке сообщений в разные соцсети и мессенджеры из одного источника

## Функционал сервиса:
- 

## Архитектура:
- Фреймворк (Django)
- БД (PostgresSQL)

## Проектная реализация:
- Сервис и база данных подняты в связанных друг с другом в контейнерах


## Запуск проекта (универсальная часть)
### Все команды выполняются в корне проекта
- Создать .env из 
```bash
cd Supportify_Backlog
cp example.env .env
```

- Добавить/обновить .env данными необходимыми для работы сервиса

- Устанавливаем make
```bash
sudo apt install -y make
```

- Авторизуемся в докерхаб (чтобы не было ограничений на скачивание образов)
```bash
docker login -u <name> -p <password>
```

- Перезапускаем докер
```bash
sudo systemctl restart docker
```

- Команда запуска сервиса из корня проекта
```bash
make run_service
```

- Проверяем запущенные контейнеры
```bash
docker ps
```

- Подключиться к контейнеру
```bash
docker exec -it supportify_backlog-app-1 bash
```

- Создаём админа
```bash
python my_site/manage.py createsuperuser
```


## Запуск проекта на удалённом сервере
- Подключиться к удалённому серверу

1. Склонировать проект на удалённом сервере:
```bash
git clone <project url>
``` 

2. Устанавливаем docker
-  Обновление системы и установка зависимостей
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
``` 

- Добавление официального GPG ключа Docker
```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
``` 

- Добавление репозитория Docker
```bash
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
``` 

- Установка Docker Engine
```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
``` 

- Использовать Docker без sudo
```bash
sudo usermod -aG docker $USER
``` 

3. Запуск проекта (универсальная часть)


4. Настраиваем внешний доступ
- Добавляем ip удалённого сервера в ALLOWED_HOSTS
```bash
nano .env
``` 

- Открываем порт 8000
```bash
sudo ufw allow 8000
``` 

- Включить UFW
```bash
sudo ufw enable
``` 

- Проверить статус
```bash
sudo ufw status
``` 

- Перезапускаем проект
```bash
make run_service
```


## Алгоритм внесения изменений на удалённый сервер
1. Внести изменения у себя на локалке
2. Закоммитить изменения 
```bash
git commit -m "Новые правки"
```
3. Залить в удаленный репозиторий
```bash
git push
```
4. Подключиться к удалённому серверу
5. Перейти в директорию с репо
```bash
cd Supportify_Backlog
```
6. Подтянуть изменения
```bash
git pull
```
7. Перезапустить сервис
```bash
make run_service
```
8. Проверить внесённые изменения
