@echo off
chcp 65001 > nul

echo ========================================
echo Установка проекта Molodoy AI
echo ========================================

echo.
echo Проверка Python...
python --version
if errorlevel 1 (
	echo Python не найден. Установите Python и добавьте его в PATH.
	pause
	exit /b 1
)

echo.
echo Создание виртуального окружения...
if not exist .venv (
	python -m venv .venv
) else (
	echo Виртуальное окружение уже существует.
)

echo.
echo Активация виртуального окружения...
call .venv\Scripts\activate.bat

echo.
echo Обновление pip...
python -m pip install --upgrade pip

echo.
echo Установка зависимостей...
pip install -r requirements.txt
if errorlevel 1 (
	echo Ошибка установки зависимостей.
	pause
	exit /b 1
)

echo.
echo Запуск PostgreSQL через Docker Compose...
docker compose up -d
if errorlevel 1 (
	echo Не удалось запустить Docker Compose.
	echo Проверьте, что Docker Desktop установлен и запущен.
	pause
	exit /b 1
)

echo.
echo ========================================
echo Установка завершена.
echo Для запуска backend используйте start.bat
echo ========================================

pause