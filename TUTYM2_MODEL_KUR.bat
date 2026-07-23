@echo off
setlocal
cd /d "%~dp0"

if "%~1"=="" (
  echo Kullanim:
  echo Indirdiginiz yolox_nano.onnx dosyasini bu BAT dosyasinin ustune surukleyip birakin.
  echo Alternatif: TUTYM2_MODEL_KUR.bat "C:\Downloads\yolox_nano.onnx"
  pause
  exit /b 1
)

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
  echo Python bulunamadi. Once Python kurulumunu tamamlayin.
  pause
  exit /b 1
)

%PYTHON_LAUNCH% scripts\install_tutym2_person_model.py "%~1"
if errorlevel 1 (
  echo Model kurulumu basarisiz. Yukaridaki hata mesajini kontrol edin.
  pause
  exit /b 1
)

echo.
echo Model hazir. TUTYM2_KONTROL.bat dosyasini yeniden acin ve Yenile dugmesine basin.
pause
