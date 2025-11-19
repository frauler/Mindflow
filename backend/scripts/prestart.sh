#! /usr/bin/env bash

set -e
set -x

# Запускаем базу данных
python app/backend_pre_start.py

# Запуск миграций
alembic upgrade head