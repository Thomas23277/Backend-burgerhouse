@echo off
chcp 65001 >nul
echo ===========================================
echo     INICIANDO BACKEND - BURGER HOUSE
echo ===========================================
echo.
cd /d "%~dp0"

:: Crear venv si no existe
if not exist "venv\Scripts\activate.bat" (
    echo [1/2] Creando entorno virtual...
    python -m venv venv
    echo [2/2] Instalando dependencias...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

echo.
echo Backend iniciado en: http://127.0.0.1:8000
echo Swagger UI: http://127.0.0.1:8000/docs
echo.
echo Presione Ctrl+C para detener
echo.
python -m uvicorn app.main:app --reload --port 8000
pause
