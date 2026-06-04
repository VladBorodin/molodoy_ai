@echo off
chcp 65001 > nul

echo ========================================
echo Запуск Molodoy AI
echo ========================================

echo.
echo Проверка виртуального окружения...
if not exist .venv (
	echo Виртуальное окружение не найдено.
	echo Сначала выполните install.bat
	pause
	exit /b 1
)

echo.
echo Запуск PostgreSQL через Docker Compose...
docker compose up -d
if errorlevel 1 (
	echo Не удалось запустить PostgreSQL.
	echo Проверьте Docker Desktop.
	pause
	exit /b 1
)

echo.
echo Активация виртуального окружения...
call .venv\Scripts\activate.bat

echo.
echo Запуск FastAPI backend...
echo Backend будет доступен по адресу:
echo http://127.0.0.1:8000
echo.
echo Swagger:
echo http://127.0.0.1:8000/docs
echo.

uvicorn app.main:app --reload

pause