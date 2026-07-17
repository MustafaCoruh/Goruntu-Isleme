@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
  echo Python bulunamadi. Once Python 3.10 veya daha yeni bir surum kurun.
  pause
  exit /b 1
)

echo T.UTYM#2 uygulamasi baslatiliyor...
start "T.UTYM#2 Sunucu" cmd /k "cd /d ""%~dp0"" && python -m uvicorn app.api.app:app --host 127.0.0.1 --port 8000"
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:8000/ui/index.html"

echo.
echo Kontrol ekrani tarayicida acildi.
echo Uygulamayi durdurmak icin T.UTYM#2 Sunucu penceresini kapatin.
pause
