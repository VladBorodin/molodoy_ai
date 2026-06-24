@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "OUT=project_tree.txt"

> "%OUT%" echo %CD%
>> "%OUT%" echo.

call :walk "." ""

echo Готово: %OUT%
exit /b

:walk
set "DIR=%~1"
set "PREFIX=%~2"

for /f "delims=" %%D in ('dir /b /ad "%DIR%" 2^>nul') do (
    if /i not "%%D"==".venv" if /i not "%%D"=="__pycache__" (
        >> "%OUT%" echo %PREFIX%[%%D]
        call :walk "%DIR%\%%D" "%PREFIX%    "
    )
)

for /f "delims=" %%F in ('dir /b /a-d "%DIR%" 2^>nul') do (
    if /i not "%%F"=="%OUT%" if /i not "%%F"=="make_tree.cmd" (
        >> "%OUT%" echo %PREFIX%%%F
    )
)

exit /b