@echo off
setlocal
cd /d "%~dp0"

echo Eski ve kullanilmayan lokal dosyalar temizleniyor...
for %%F in ("app\ui\static\tutym2_*.html") do if exist "%%~F" del /q "%%~F"
for /r %%F in (.gitkeep) do if exist "%%~F" del /q "%%~F"

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

echo 8000 portunda kalmis eski T.UTYM#2 sunucusu kapatiliyor...
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":8000 .*LISTENING"') do (
  echo Eski sunucu PID %%P kapatiliyor...
  taskkill /PID %%P /F >nul 2>nul
)
timeout /t 2 /nobreak >nul

echo T.UTYM#2 uygulamasinin guncel surumu baslatiliyor...
start "T.UTYM#2 Sunucu" cmd /k "cd /d ""%~dp0"" && %PYTHON_LAUNCH% -m uvicorn app.api.app:app --host 127.0.0.1 --port 8000"
echo Guncel API hazir olana kadar bekleniyor...
powershell -NoProfile -Command "$deadline = (Get-Date).AddSeconds(20); $ok = $false; while ((Get-Date) -lt $deadline -and -not $ok) { try { $schema = Invoke-RestMethod 'http://127.0.0.1:8000/openapi.json' -TimeoutSec 2; $ok = $schema.paths.PSObject.Properties.Name -contains '/product/calibration-frame' } catch { }; if (-not $ok) { Start-Sleep -Milliseconds 500 } }; if ($ok) { exit 0 } else { exit 1 }"
if errorlevel 1 (
  echo UYARI: Guncel API 20 saniyede dogrulanamadi.
  echo Tarayici yine de acilacak. Sunucu penceresindeki hatayi kontrol edip sayfayi yenileyin.
)
start "" "http://127.0.0.1:8000/ui/index.html?v=%RANDOM%"

echo.
echo Kontrol ekrani tarayicida acildi.
echo Uygulamayi durdurmak icin T.UTYM#2 Sunucu penceresini kapatin.
pause
