@echo off
setlocal
cd /d "%~dp0"

set "PYTHON_LAUNCH="

if exist ".venv\Scripts\python.exe" set "PYTHON_LAUNCH=""%CD%\.venv\Scripts\python.exe"""

if not defined PYTHON_LAUNCH (
  python --version >nul 2>nul
  if not errorlevel 1 set "PYTHON_LAUNCH=python"
)

if not defined PYTHON_LAUNCH (
  py -3 --version >nul 2>nul
  if not errorlevel 1 set "PYTHON_LAUNCH=py -3"
)

if not defined PYTHON_LAUNCH (
  echo Python calistirilamadi.
  echo Python yukluyse Windows'ta "Add Python to PATH" secenegini etkinlestirin
  echo veya Python Launcher ^(py.exe^) kurulumunu tamamlayin.
  pause
  exit /b 1
)

%PYTHON_LAUNCH% -c "import uvicorn" >nul 2>nul
if errorlevel 1 (
  echo Gerekli Python paketleri bulunamadi.
  choice /M "requirements.txt paketleri simdi kurulsun mu"
  if errorlevel 2 exit /b 1
  %PYTHON_LAUNCH% -m pip install -r requirements.txt
  if errorlevel 1 (
    echo Paket kurulumu basarisiz oldu.
    pause
    exit /b 1
  )
)

echo T.UTYM#2 uygulamasi baslatiliyor...
start "T.UTYM#2 Sunucu" cmd /k "cd /d ""%~dp0"" && %PYTHON_LAUNCH% -m uvicorn app.api.app:app --host 127.0.0.1 --port 8000"
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:8000/ui/index.html"

echo.
echo Kontrol ekrani tarayicida acildi.
echo Uygulamayi durdurmak icin T.UTYM#2 Sunucu penceresini kapatin.
pause
