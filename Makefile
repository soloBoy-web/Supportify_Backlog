SHELL := /bin/bash

.PHONY: install_python create_env sync_all clean_env init_env run_service

DOCKER_COMPOSE_MAIN = docker-compose.yml
ENV_FILE ?= .env
DOCKER_COMPOSE_MAIN_CMD = docker compose -f $(DOCKER_COMPOSE_MAIN) --env-file ${ENV_FILE}
VENV_DIR = .venv

# Путь к интерпретатору в виртуальном окружении
VENV_PYTHON = $(VENV_DIR)/bin/python
VENV_PIP = $(VENV_DIR)/bin/pip


# Подготовить виртуальное окружение
create_env: clean_env
	python3 -m venv $(VENV_DIR)

# Установить зависимости через poetry
sync_all: create_env
	@echo "🔹 Устанавливаем зависимости..."
	$(VENV_PIP) install -r requirements.txt

# Очистка
clean_env:
	@echo "🔸 Удаляем виртуальное окружение..."
	@rm -rf $(VENV_DIR)

# Полная инициализация
init_env: clean_env create_env sync_all
	@echo "✅ Локальное окружение готово к работе!"


# Запуск сервиса
fix_permissions:
	chmod 755 prestart.sh

run_service: fix_permissions
	$(DOCKER_COMPOSE_MAIN_CMD) up app -d --build


# Команды остановки
stop_all:
	@echo "Остановка всех контейнеров..."
	@docker ps -q | xargs docker stop
	@echo "Все контейнеры остановлены."

stop_all_and_remove:
	@echo "Остановка и удаление всех контейнеров..."
	@docker ps -aq | xargs docker stop
	@docker ps -aq | xargs docker rm
	@echo "Все контейнеры удалены."


# Служебные
show_general_size_info:
	docker system df -v

show_containers_size:
	docker container ls -a -s --format "table {{.Names}}\t{{.Size}}"

show_images_size:
	docker image ls --format "table {{.Repository}}\t{{.Size}}"

show_dangling_images:
	docker images -f dangling=true

delete_dangling_images:
	docker image prune -f
